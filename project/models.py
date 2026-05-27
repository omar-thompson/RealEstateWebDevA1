from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_row):
        self.id = user_row[0]                      # user_id (required by Flask-Login)
        self.full_name = user_row[1]
        self.email = user_row[2]
        self.phone_number = user_row[3]
        self.password_hash = user_row[4]
        self.prefers_pets = bool(user_row[5])
        self.prefers_social_lifestyle = bool(user_row[6])
        self.description = user_row[7]
        self.role = user_row[8]
        self.created_at = user_row[9]