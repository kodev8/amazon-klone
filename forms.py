from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
import re
from datetime import datetime

class Formatter():
    
    def format_lower(name):
        return name.lower().strip() if isinstance(name, str) else name
    
    def format_title(name):
        return re.sub(' +', ' ', name.title()).strip() if isinstance(name, str) else name
    
    def format_strip(name):
        return name.strip() if isinstance(name, str) else name
    
class Validator:

    _email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
    _password_pattern = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9\s]).{8,}'
    _name_pattern = r'^[a-zA-z][a-zA-z-.\'\s]*[a-zA-z]?$'
    _username_pattern = r'^[a-zA-z0-9-_\.]+$'

    @staticmethod
    def validate_name(form, name):
        if not re.fullmatch(Validator._name_pattern, name.data):
            raise ValidationError('Invalid name')

    @staticmethod
    def validate_email(form, email):
        if not re.fullmatch(Validator._email_pattern, email.data):
            raise ValidationError('Invalid email')

    @staticmethod
    def validate_password(form, password):
        if not re.fullmatch(Validator._password_pattern, password.data):
            raise ValidationError('Password must contain: at least 8 characters, 1 lower case, 1 uppercase, 1 number and 1 special character')

    @staticmethod
    def validate_username(form, user):
        if not re.fullmatch(Validator._username_pattern, user.data):
            raise ValidationError('Username must only contain letters, numbers, periods and underscores')


# CUSTOM DATA REQUIRED
class customDR(DataRequired):
    def __init__(self, message=None):
        super().__init__(message)

    def __call__(self, form, field):

        field_label = field.label.text
    
        if self.message is None and field_label:

            self.message = f"{field_label} is required"

        super().__call__(form, field)



class OrderedForm(FlaskForm):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __iter__(self):
        fields = list(super().__iter__())
        field_dict = {field.id: field for field in fields}
        for field_id in self._order:
            if field_id in field_dict:
                yield field_dict[field_id]

# LOGIN FORM
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[customDR()], filters=[Formatter.format_lower])
    password = PasswordField('Password', validators=[customDR()])
    log_in = SubmitField('Sign In')

# create sub for address
class ProfileCommonFields:
    fname = StringField('First Name', validators=[customDR(), Length(min=1, max=50), Validator.validate_name], filters=[Formatter.format_title])
    lname = StringField('Last Name', validators=[customDR(), Length(min=1, max=50), Validator.validate_name], filters=[Formatter.format_title])
    dob = DateField('Date of Birth', validators=[customDR(), ],)
    
    def validate_dob(form, field):
        today = datetime.today()
        min_year = today.year - 16
        min_age_date = datetime(min_year, today.month, today.day).date()
        if field.data >  min_age_date:
            raise ValidationError("You must be 16 or older to enter.")


class PasswordFields:
    password = PasswordField('Password', 
                            validators=[ customDR(), 
                                            EqualTo('conf_password', message="Passwords must match"), 
                                            Validator.validate_password
                                        ]
                                )
    conf_password = PasswordField('Confirm Password', validators=[customDR()])
    
# REGISTER FORM
class RegisterForm(OrderedForm, ProfileCommonFields, PasswordFields):

    email = EmailField('Email', validators=[customDR(), Email()], filters=[Formatter.format_lower])
    register = SubmitField('Create Your Account')
    
    _order = ('csrf_token', 'fname', 'lname', 'username', 'email', 'dob', 'password', 'conf_password', 'register')

# Account Form
class AccountForm(OrderedForm, ProfileCommonFields, ):
    email = EmailField('Email', validators=[customDR(), Email()], filters=[Formatter.format_lower])

    update = SubmitField('Done')

    _order = ('csrf_token', 'fname', 'lname', 'username', 'email', 'dob', 'update')

class AddressForm(FlaskForm):
    line1 =  StringField('Address Line 1',validators=[customDR(), Length(max=50)] , filters=[Formatter.format_title] )
    city =  StringField('City',validators=[customDR(), Length(max=50)] , filters=[Formatter.format_title])
    country =  StringField('Country', validators=[customDR(),Length(max=50)] , filters=[Formatter.format_title])
    zip_code =  StringField('Zip/Postal Code', validators=[customDR(),Length(max=10)]  , filters=[Formatter.format_lower])
    add = SubmitField('Confirm')
    

# Reset Passowrd
class ResetPasswordForm(OrderedForm, PasswordFields):
    old_password = PasswordField('Old Password', validators=[customDR()])
    _order = ('csrf_token', 'old_password', 'password', 'conf_password')

# CSERV FORM
class CServForm(FlaskForm):
    email =     email = EmailField('Email', filters=[Formatter.format_lower], render_kw={'disabled':''})
    message = TextAreaField('Share Your Concerns...', validators=[customDR(), Length(min=1,max=200)], filters=[Formatter.format_strip])
    send_message = SubmitField('Send Message')
    
    _order = ('csrf_token', 'old_password', 'password', 'conf_password')




    
