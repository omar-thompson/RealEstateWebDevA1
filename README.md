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

python -m venv venv
source venv\Scripts\activate

### Step 3: Install dependencies 

pip install -r requirements.txt

### Step 4: Set up the database (Important)

This project uses MySQL Workbench

4.1 Create the database (Open mysql/workbench)
CREATE DATABASE realestate_db;

4.2 Import Schema 
Option 1 

mysql -u root -p realestate_db < project/database.sql

Option 2

Open MySQL Workbench
Select your database
Run contents of project/database.sql (as in copy and paste all of the commands in database.sql to run in workbench under the realestate_db database)

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
app.config['MYSQL_PASSWORD'] = 'your_password' ## Rename this to what your computer password is  
app.config['MYSQL_DB'] = 'real_estate_db' ## Rename this to what you you name your database 


### Step 6: Run the application 
In your terminal run the application with the following command: 

python run.py


#### NOTE!!! Please know that if you are running this for the first time it may take a while due to a cold first connection! 
#### Just run the file and wait as the MySQL connection is cold, and the first query takes time. 
### Step 7: Open in browser

http://127.0.0.1:5000/

### Step 8: Default test accounts
#### Admin Accounts Login details 
Email login - admin@test.com 
Email login - admin2@test.com
Password for both: password

#### Sharer/Seller Login details 
Email login - sharer1@test.com
Email login - sharer2@test.com
Password for both: password 

#### Seeker/Buyer Login Details 
Email login - buyer1@test.com
Email login - buyer2@test.com
Password for both: password 



Please note when you are fully completed with the application dont forget to deactivate the virtual environment by entering 

deactivate 

In your terminal (you can confirm this as "venv" would have dissappered at the beginning of your command line)