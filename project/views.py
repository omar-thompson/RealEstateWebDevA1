# The Views module defines the routes and view functions for the Flask application. Each route corresponds to a specific URL endpoint and renders the appropriate HTML template. The test_db route is included to verify the database connection.

from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from project import app, mysql


# Home Page route - renders the home.html template
@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT
        l.listing_id,
        l.title,
        l.description,
        l.weekly_price,
        l.availability_status,
        p.suburb,
        p.image_url
    FROM listings l
    JOIN properties p ON l.property_id = p.property_id
    LIMIT 6
""")
    columns = [col[0] for col in cur.description]

    listings = [
        dict(zip(columns, row))
        for row in cur.fetchall()
    ]
    cur.close()
    return render_template("home.html", listings=listings)

@app.route('/bookmarks')
def bookmarks():
    return render_template("bookmarks.html")

@app.route('/listing')
def listing():
    return render_template("listing.html")

@app.route('/person_details')
def person_details():
    return render_template("person_details.html")

@app.route('/property_details')
def property_details():
    return render_template("property_details.html") 

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

        hashed_password = generate_password_hash(password)

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO users (full_name, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
        """, (full_name, email, hashed_password, 'seeker'))

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