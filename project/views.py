# The Views module defines the routes and view functions for the Flask application. Each route corresponds to a specific URL endpoint and renders the appropriate HTML template. The test_db route is included to verify the database connection.

from flask import render_template, request, redirect, url_for, session, flash
from flask_login import current_user
from flask_wtf import form
from werkzeug.security import generate_password_hash, check_password_hash
from project import app, mysql
from project.forms import EnquiryForm, PropertyFilterForm


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
        WHERE 1=1
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

@app.route('/bookmarks')
def bookmarks():
    return render_template("bookmarks.html")

@app.route('/listing')
def listing():
    return render_template("listing.html")

## This route displays the properties that the currently logged-in user has. It checks if the user is authenticated, retrieves the properties from the database where the sharer_id matches the user's ID, and renders the my_properties.html template with the retrieved data.
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

    return render_template("my_properties.html", properties=properties)

@app.route('/property/create', methods=['GET', 'POST'])
def create_property():
    if 'user_id' not in session:
        return redirect(url_for('login'))

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

    return render_template("create_property.html")


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

    return render_template("edit_listing.html", listing=listing)

## This route handles the property details page. It retrieves the listing and associated property information from the database based on the listing_id provided in the URL. If the listing is found, it renders the property_details.html template with the listing data and an enquiry form. If the form is submitted, it inserts a new enquiry into the database.
@app.route('/property/<int:listing_id>')
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
        return "Listing not found", 404
    
    columns = [col[0] for col in cur.description]
    listing = dict(zip(columns, row))

    cur.close()

    form = EnquiryForm()

    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        cur.execute(""" 
            INSERT INTO enquiries (user_id, listing_id, message, status) 
            VALUES (%s, %s, %s, %s) 
        """, (
        session.get('user_id'),
        listing_id,
        form.message.data
        ))
        mysql.connection.commit()
        cur.close()
        flash("Enquiry sent successfully")

    return render_template("property_details.html", listing=listing, form=form)

@app.route('/test-db')
def test_db():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT DATABASE();")
        result = cur.fetchone()
        return f"Connected successfully: {result}"
    except Exception as e:
        return f"Connection failed: {str(e)}"
    

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

    return render_template('register.html')

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

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))