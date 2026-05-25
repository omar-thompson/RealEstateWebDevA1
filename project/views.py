# The Views module defines the routes and view functions for the Flask application. Each route corresponds to a specific URL endpoint and renders the appropriate HTML template. The test_db route is included to verify the database connection.

from flask import render_template
from project import app, mysql

# Home Page route - renders the home.html template
@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute(
        """
        SELECT
            l.listing_id,
            l.title,
            l.description,
            l.weekly_price,
            p.image_url
        FROM listings l
        JOIN properties p ON l.property_id = p.property_id
        LIMIT 6
        """
        )
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