from flask import Flask
from flask_mysqldb import MySQL


app = Flask(__name__)

# Security Key used for session management and other security-related features in Flask.
app.config['SECRET_KEY'] = 'your_secret_key'

# MySQL database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '6351284790Aa!'      
app.config['MYSQL_DB'] = 'realestate_db'

mysql = MySQL(app)


#import routes after app + mysql initialization
from project import views