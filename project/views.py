# The Views module defines the routes and view functions for the Flask application. Each route corresponds to a specific URL endpoint and renders the appropriate HTML template. The test_db route is included to verify the database connection. this is arguably the most important page, this is where i ensure that connections to every link go somewhere and that the correct data is being passed to the templates. This is also where i handle all the form submissions and database interactions for the application. be careful here, this is where most of the logic of the application is. Additionally if i decide to add more features, put it in a new folder i will have to ensure that the route includes the folder as well. 

from flask import render_template, request, redirect, url_for, session, flash
from flask_login import current_user
from flask_wtf import form
from werkzeug.security import generate_password_hash, check_password_hash
from project import app, mysql
from project.forms import EnquiryForm, PropertyFilterForm

## Confirms connection to the database 
@app.route('/test-db')
def test_db():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT DATABASE();")
        result = cur.fetchone()
        return f"Connected successfully: {result}"
    except Exception as e:
        return f"Connection failed: {str(e)}"

## This section defines the main route for the home page, which displays property listings. It constructs a dynamic SQL query based on the filters provided by the user through the PropertyFilterForm. The results are fetched from the database and passed to the home.html template for rendering.
@app.route('/')
def home():
    form = PropertyFilterForm(request.args)

    cur = mysql.connection.cursor()

    query = """
        SELECT
            l.listing_id,
            l.title,
            l.description,
            l.weekly_price,
            l.bills_included,
            l.available_rooms,
            l.preferred_gender,
            p.suburb,
            p.image_url,
            p.bedrooms,
            p.bathrooms,
            p.pet_friendly,
            p.lifestyle_type
        FROM listings l
        JOIN properties p ON l.property_id = p.property_id
        WHERE l.availability_status = 'available'
    """

    params = []

    # This is for my filtering functionality on the home page. It checks if each filter field has a value and appends the appropriate SQL condition to the query, along with the corresponding parameter value.
    if form.min_price.data:
        query += " AND l.weekly_price >= %s"
        params.append(form.min_price.data)

    if form.max_price.data:
        query += " AND l.weekly_price <= %s"
        params.append(form.max_price.data)

    if form.bedrooms.data:
        query += " AND p.bedrooms >= %s"
        params.append(form.bedrooms.data)

    if form.bathrooms.data:
        query += " AND p.bathrooms >= %s"
        params.append(form.bathrooms.data)

    if form.pet.data in ['0', '1']:
        query += " AND p.pet_friendly = %s"
        params.append(int(form.pet.data))

    if form.gender.data:
        query += " AND l.preferred_gender = %s"
        params.append(form.gender.data)

    if form.lifestyle.data:
        query += " AND p.lifestyle_type = %s"
        params.append(form.lifestyle.data)

    if form.bills.data in ['0', '1']:
        query += " AND l.bills_included = %s"
        params.append(int(form.bills.data))

    cur.execute(query, tuple(params))

    columns = [col[0] for col in cur.description]
    listings = [dict(zip(columns, row)) for row in cur.fetchall()]

    cur.close()

    return render_template("home.html", listings=listings, form=form)


## This route renders the bookmarks page used by Seekers to view their favourite listing they have saved
@app.route('/bookmarks')
def bookmarks():

    # Must be logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    # Get all saved listings for this user
    cur.execute("""
        SELECT
            l.listing_id,
            l.title,
            l.description,
            l.weekly_price,
            l.availability_status,
            p.address,
            p.suburb,
            p.state,
            p.bedrooms,
            p.bathrooms,
            p.pet_friendly,
            p.lifestyle_type,
            p.property_type,
            p.image_url,
            sl.date_saved
        FROM saved_listings sl
        JOIN listings l ON sl.listing_id = l.listing_id
        JOIN properties p ON l.property_id = p.property_id
        WHERE sl.user_id = %s
        ORDER BY sl.date_saved DESC
    """, (session['user_id'],))

    rows = cur.fetchall()

    columns = [col[0] for col in cur.description]
    bookmarks = [dict(zip(columns, row)) for row in rows]

    cur.close()

    return render_template("seeker/bookmarks.html", bookmarks=bookmarks)


## The following 10 routes, handle the property management pagees for sharers and some of the functions that are associated. 
@app.route('/my_properties')
def my_properties():

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT 
            p.property_id,
            p.address,
            p.suburb,
            p.state,
            p.bedrooms,
            p.bathrooms,
            l.listing_id,
            l.availability_status,
            l.weekly_price,
            l.title
        FROM properties p
        LEFT JOIN listings l ON p.property_id = l.property_id
        WHERE p.sharer_id = %s
    """, (session['user_id'],))

    columns = [col[0] for col in cur.description]
    properties = [dict(zip(columns, row)) for row in cur.fetchall()]

    cur.close()

    return render_template("sharer/my_properties.html", properties=properties)

@app.route('/property/create', methods=['GET', 'POST'])
def create_property():
    if 'user_id' not in session:
        return redirect(url_for('auth/login'))

    if request.method == 'POST':
        address = request.form['address']
        suburb = request.form['suburb']
        state = request.form['state']
        bedrooms = request.form['bedrooms']
        bathrooms = request.form['bathrooms']
        pet_friendly = request.form.get('pet_friendly') == 'on'
        lifestyle_type = request.form['lifestyle_type']
        property_type = request.form['property_type']
        image_url = request.form['image_url']

        cur = mysql.connection.cursor()

        # 1. Create property
        cur.execute("""
            INSERT INTO properties (
                sharer_id, address, suburb, state,
                bedrooms, bathrooms, pet_friendly,
                lifestyle_type, property_type, image_url
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            session['user_id'],
            address,
            suburb,
            state,
            bedrooms,
            bathrooms,
            pet_friendly,
            lifestyle_type,
            property_type,
            image_url
        ))

        property_id = cur.lastrowid

        # 2. Auto-create listing (PLACEHOLDERS)
        cur.execute("""
            INSERT INTO listings (
                property_id,
                title,
                description,
                weekly_price,
                bills_included,
                available_rooms,
                preferred_gender,
                availability_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            property_id,
            "New Listing",
            "No description yet",
            0,
            False,
            1,
            "any",
            "pending"
        ))

        mysql.connection.commit()
        cur.close()

        flash("Property and listing created successfully")
        return redirect(url_for('my_properties'))

    return render_template("sharer/create_property.html")

@app.route('/property/<int:property_id>/publish')
def publish(property_id):

    cur = mysql.connection.cursor()

    cur.execute("""
        UPDATE listings
        SET availability_status = 'available'
        WHERE property_id = %s
    """, (property_id,))

    mysql.connection.commit()
    cur.close()

    return redirect(url_for('my_properties'))

@app.route('/property/<int:property_id>/unpublish')
def unpublish(property_id):

    cur = mysql.connection.cursor()

    cur.execute("""
        UPDATE listings
        SET availability_status = 'pending'
        WHERE property_id = %s
    """, (property_id,))

    mysql.connection.commit()
    cur.close()

    return redirect(url_for('my_properties'))

@app.route('/listing/<int:listing_id>/edit', methods=['GET', 'POST'])
def edit_listing(listing_id):

    cur = mysql.connection.cursor()

    # GET existing listing
    cur.execute("""
        SELECT *
        FROM listings
        WHERE listing_id = %s
    """, (listing_id,))

    row = cur.fetchone()

    if not row:
        return "Listing not found", 404

    columns = [col[0] for col in cur.description]
    listing = dict(zip(columns, row))

    if request.method == 'POST':

        title = request.form['title']
        description = request.form['description']
        weekly_price = request.form['weekly_price']
        bills_included = request.form.get('bills_included') == 'on'
        available_rooms = request.form['available_rooms']
        preferred_gender = request.form['preferred_gender']

        cur.execute("""
            UPDATE listings
            SET title = %s,
                description = %s,
                weekly_price = %s,
                bills_included = %s,
                available_rooms = %s,
                preferred_gender = %s
            WHERE listing_id = %s
        """, (
            title,
            description,
            weekly_price,
            bills_included,
            available_rooms,
            preferred_gender,
            listing_id
        ))

        mysql.connection.commit()
        cur.close()

        return redirect(url_for('my_properties'))

    cur.close()

    return render_template("sharer/edit_listing.html", listing=listing)

@app.route('/property/<int:property_id>/delete')
def delete_property(property_id):

    cur = mysql.connection.cursor()

    # delete listing first
    cur.execute("""
        DELETE FROM listings
        WHERE property_id = %s
    """, (property_id,))

    # then delete property
    cur.execute("""
        DELETE FROM properties
        WHERE property_id = %s
    """, (property_id,))

    mysql.connection.commit()
    cur.close()

    flash("Property deleted successfully")

    return redirect(url_for('my_properties'))

@app.route('/property/<int:property_id>/edit', methods=['GET', 'POST'])
def edit_property(property_id):

    cur = mysql.connection.cursor()

    # Load the property by property_id (NOT sharer_id)
    cur.execute("""
        SELECT 
            p.property_id,
            p.address,
            p.suburb,
            p.state,
            p.bedrooms,
            p.bathrooms,
            p.pet_friendly,
            p.lifestyle_type,
            p.property_type,
            p.image_url,
            p.sharer_id
        FROM properties p
        WHERE p.property_id = %s
    """, (property_id,))

    row = cur.fetchone()

    if not row:
        cur.close()
        return "Property not found", 404

    columns = [col[0] for col in cur.description]
    property_data = dict(zip(columns, row))

    # 🔒 Ownership check
    if property_data['sharer_id'] != session['user_id']:
        cur.close()
        return "Unauthorized", 403

    # =========================
    # HANDLE FORM SUBMISSION
    # =========================
    if request.method == 'POST':

        address = request.form['address']
        suburb = request.form['suburb']
        state = request.form['state']
        bedrooms = request.form['bedrooms']
        bathrooms = request.form['bathrooms']

        # checkbox fix
        pet_friendly = 1 if request.form.get('pet_friendly') == 'on' else 0

        lifestyle_type = request.form['lifestyle_type']
        property_type = request.form['property_type']
        image_url = request.form['image_url']

        cur.execute("""
            UPDATE properties
            SET address = %s,
                suburb = %s,
                state = %s,
                bedrooms = %s,
                bathrooms = %s,
                pet_friendly = %s,
                lifestyle_type = %s,
                property_type = %s,
                image_url = %s
            WHERE property_id = %s
        """, (
            address,
            suburb,
            state,
            bedrooms,
            bathrooms,
            pet_friendly,
            lifestyle_type,
            property_type,
            image_url,
            property_id
        ))

        mysql.connection.commit()
        cur.close()

        flash("Property updated successfully")
        return redirect(url_for('my_properties'))

    cur.close()

    return render_template("sharer/edit_property.html", property=property_data)

@app.route('/my-applications')
def my_applications():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'sharer':
        return "Unauthorized", 403

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT
            a.application_id,
            a.introduction_message,
            a.status,
            a.created_at,
            l.title
        FROM applications a
        JOIN listings l ON a.listing_id = l.listing_id
        JOIN properties p ON l.property_id = p.property_id
        WHERE p.sharer_id = %s
        ORDER BY a.created_at DESC
    """, (session['user_id'],))

    rows = cur.fetchall()
    cols = [col[0] for col in cur.description]
    applications = [dict(zip(cols, r)) for r in rows]

    cur.close()

    return render_template("sharer/my_applications.html", applications=applications)

@app.route('/application/<int:application_id>/reject')
def reject_application(application_id):

    if session.get('role') != 'sharer':
        return "Unauthorized", 403

    cur = mysql.connection.cursor()

    cur.execute("""
        UPDATE applications a
        JOIN listings l
            ON a.listing_id = l.listing_id
        JOIN properties p
            ON l.property_id = p.property_id
        SET a.status = 'rejected'
        WHERE a.application_id = %s
          AND p.sharer_id = %s
    """, (
        application_id,
        session['user_id']
    ))

    mysql.connection.commit()
    cur.close()

    return redirect(url_for('my_applications'))

@app.route('/application/<int:application_id>/accept')
def accept_application(application_id):

    print("Accepting application:", application_id)

    cur = mysql.connection.cursor()

    try:
        cur.execute("""
            UPDATE applications
            SET status = 'accepted'
            WHERE application_id = %s
        """, (application_id,))

        mysql.connection.commit()

    except Exception as e:
        print("ERROR:", e)
        mysql.connection.rollback()

    finally:
        cur.close()

    return redirect(url_for('my_applications'))

## The following 3 routes handle the propdetails, saving the property and unsaving the property. 
@app.route('/property/<int:listing_id>', methods=['GET', 'POST'])
def property_details(listing_id):

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT
            l.listing_id,
            l.title,
            l.description,
            l.weekly_price,
            l.bills_included,
            l.available_rooms,
            l.preferred_gender,
            l.availability_status,
            p.address,
            p.suburb,
            p.state,
            p.bedrooms,
            p.bathrooms,
            p.pet_friendly,
            p.lifestyle_type,
            p.property_type,
            p.image_url
        FROM listings l
        JOIN properties p ON l.property_id = p.property_id
        WHERE l.listing_id = %s
    """, (listing_id,))

    row = cur.fetchone()

    if not row:
        cur.close()
        return "Listing not found", 404

    columns = [col[0] for col in cur.description]
    listing = dict(zip(columns, row))

    saved = False

    if 'user_id' in session:
        cur.execute("""
            SELECT 1
            FROM saved_listings
            WHERE user_id = %s
              AND listing_id = %s
        """, (session['user_id'], listing_id))

        saved = cur.fetchone() is not None


    form = EnquiryForm()

    if form.validate_on_submit():

        cur.execute("""
            INSERT INTO applications (seeker_id, listing_id, introduction_message, status)
            VALUES (%s, %s, %s, %s)
        """, (
            session.get('user_id'),
            listing_id,
            form.message.data,
            'pending'
        ))

        mysql.connection.commit()
        flash("Enquiry sent successfully")

    cur.close()

    return render_template(
        "property_details.html",
        listing=listing,
        form=form,
        saved=saved
    )

@app.route('/property/<int:listing_id>/save')
def save_listing(listing_id):

    if 'user_id' not in session:
        return redirect(url_for('login', next=request.url))

    cur = mysql.connection.cursor()

    cur.execute("""
        INSERT IGNORE INTO saved_listings (user_id, listing_id)
        VALUES (%s, %s)
    """, (session['user_id'], listing_id))

    mysql.connection.commit()
    cur.close()

    return redirect(url_for('property_details', listing_id=listing_id))

@app.route('/property/<int:listing_id>/unsave')
def unsave_listing(listing_id):

    if 'user_id' not in session:
        return redirect(url_for('auth/login'))

    cur = mysql.connection.cursor()

    cur.execute("""
        DELETE FROM saved_listings
        WHERE user_id = %s AND listing_id = %s
    """, (session['user_id'], listing_id))

    mysql.connection.commit()
    cur.close()

    return redirect(request.referrer or url_for('home'))


## This section handles user registration, login, and logout functionality. It uses password hashing for security and manages user sessions.
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        hashed_password = generate_password_hash(password)

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO users (full_name, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
        """, (full_name, email, hashed_password, role))

        mysql.connection.commit()
        cur.close()

        flash("Account created successfully")
        return redirect(url_for('login'))

    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT *
            FROM users
            WHERE email = %s
        """, (email,))

        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[4], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['role'] = user[8]

            return redirect(url_for('home'))
        else:
            flash("Invalid login details")

    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


## The following two sections handles errors
@app.errorhandler(404)
def page_not_found(request):
    return render_template('errors/404.html', status=404)

@app.errorhandler(500)
def internal_server_error(request):
    return render_template('errors/500.html', status=500)  


## the following  5 pages is for the admin managment page. 
@app.route('/management')
def management():
    if session.get('role') != 'admin':
        return "Unauthorized", 403
    
    cur = mysql.connection.cursor()

    #gets the users
    cur.execute("""
        SELECT user_id, full_name, email, role, created_at
        FROM users
        ORDER BY created_at DESC
    """)

    users = cur.fetchall()
    columns = [col[0] for col in cur.description]
    users = [dict(zip(columns, row)) for row in users]

    #gets the listings
    cur.execute("""
        SELECT listing_id, title, weekly_price, availability_status, created_at
        FROM listings
        ORDER BY created_at DESC
    """)

    listings = cur.fetchall()
    listings_columns = [col[0] for col in cur.description]
    listings = [dict(zip(listings_columns, row)) for row in listings]

    cur.close()

    return render_template("admin/management.html", users=users, listings=listings)

@app.route('/admin/user/create', methods=['GET', 'POST'])
def create_user():

    if session.get('role') != 'admin':
        return "Unauthorized", 403

    if request.method == 'POST':

        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        hashed = generate_password_hash(password)

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO users (full_name, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
        """, (full_name, email, hashed, role))

        mysql.connection.commit()
        cur.close()

        return redirect(url_for('management'))

    return render_template("admin/create_user.html")

@app.route('/admin/user/<int:user_id>/delete')
def delete_user(user_id):

    if session.get('role') != 'admin':
        return "Unauthorized", 403

    cur = mysql.connection.cursor()

    # I need to delete all saved listings for this user then delete properties, then the user itself. This is to avoid foreign key constraint errors. and cascade errors.
    cur.execute("""
        DELETE l FROM listings l
        JOIN properties p ON l.property_id = p.property_id
        WHERE p.sharer_id = %s
    """, (user_id,))

    cur.execute("""
        DELETE FROM properties
        WHERE sharer_id = %s
    """, (user_id,))

    cur.execute("""
        DELETE FROM users
        WHERE user_id = %s
    """, (user_id,))

    mysql.connection.commit()
    cur.close()

    return redirect(url_for('management'))

@app.route('/admin/listing/<int:listing_id>/publish')
def admin_publish(listing_id):

    if session.get('role') != 'admin':
        return "Unauthorized", 403

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE listings
        SET availability_status = 'available'
        WHERE listing_id = %s
    """, (listing_id,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('management'))

@app.route('/admin/listing/<int:listing_id>/unpublish')
def admin_unpublish(listing_id):

    if session.get('role') != 'admin':
        return "Unauthorized", 403

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE listings
        SET availability_status = 'pending'
        WHERE listing_id = %s
    """, (listing_id,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('management'))