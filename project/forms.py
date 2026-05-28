from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, StringField, TextAreaField
from wtforms.validators import Optional, DataRequired, Email


## Filters for Home Page 
class PropertyFilterForm(FlaskForm):
    min_price = DecimalField('Min Price', validators=[Optional()])
    max_price = DecimalField('Max Price', validators=[Optional()])

    bedrooms = SelectField(
        'Bedrooms',
        choices=[
            ('', 'Any'),
            ('1', '1+'),
            ('2', '2+'),
            ('3', '3+')
        ],
        validators=[Optional()]
    )

    bathrooms = SelectField(
        'Bathrooms',
        choices=[
            ('', 'Any'),
            ('1', '1+'),
            ('2', '2+')
        ],
        validators=[Optional()]
    )

    pet = SelectField(
        'Pet Friendly',
        choices=[
            ('', 'Any'),
            ('1', 'Yes'),
            ('0', 'No')
        ],
        validators=[Optional()]
    )

    gender = SelectField(
        'Preferred Gender',
        choices=[
            ('', 'Any'),
            ('male', 'Male'),
            ('female', 'Female'),
            ('any', 'Any')
        ],
        validators=[Optional()]
    )

    lifestyle = SelectField(
        'Lifestyle',
        choices=[
            ('', 'Any'),
            ('social', 'Social'),
            ('quiet', 'Quiet')
        ],
        validators=[Optional()]
    )

    bills = SelectField(
        'Bills Included',
        choices=[
            ('', 'Any'),
            ('1', 'Yes'),
            ('0', 'No')
        ],
        validators=[Optional()]
    )

## Enquiry form for listings 
class EnquiryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])