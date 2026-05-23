# Random Change 
from flask import render_template
from project import app

@app.route('/')
def home():
    return render_template('home.html')

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