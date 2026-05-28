# Real Estate Web Development 
## Brief setup instructions 

### Step 1: Clone the Project 

git clone <your-repo-url>
cd RealEstateWebDevA1

### Step 2: Create virtual environment 

macOS/Linux:

python3 -m venv venv
source venv/bin/activate

Windows:

python3 -m venv venv
source venv/bin/activate



### Step 3: Install dependencies 

pip install -r requirements.txt

### Step 4: Set up the database (Important)

This project uses MySQL

4.1 Create the database (Open mysql/workbench)
CREATE DATABASE realestate_db;

4.2 Import Schema 
Option 1 

mysql -u root -p realestate_db < project/database.sql

Option 2 (easier)

Open MySQL Workbench
Select your database
Run contents of project/database.sql (as in copy and paste all of the commands in database.sql)

4.3 Verify the tables have been made 

Ensure the following tables exist:
users
properties
listings
applications (if included)


### Step 5: Configure the application 
Check project/__init__.py for database settings such as 

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'your_password' ## This part here make sure its your password you log into your computer with 
app.config['MYSQL_DB'] = 'real_estate_db'


### Step 6: Run the application 
In your terminal run the application with the following command: 

python run.py

### Step 7: Open in browser

http://127.0.0.1:5000/

### Step 8: Default test accounts
Email: any of the test emails 
Password: password




