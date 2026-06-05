## I used this page to create the initial hashed passwords for the dummy info in the database for the users, i made all the passwords "password".

from werkzeug.security import generate_password_hash

print(generate_password_hash("password"))