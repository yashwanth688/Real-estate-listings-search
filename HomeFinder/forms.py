from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, FloatField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    role = SelectField('Role', choices=[('user', 'User'), ('agent', 'Agent')], default='user')
    submit = SubmitField('Register')

class ProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Update Profile')

class PropertyForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=150)])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=1)])
    location = StringField('Location', validators=[DataRequired(), Length(max=150)])
    property_type = SelectField('Type', choices=[('Apartment', 'Apartment'), ('House', 'House'), ('Villa', 'Villa'), ('Plot', 'Plot'), ('Commercial', 'Commercial')], validators=[DataRequired()])
    status = SelectField('Status', choices=[('Sale', 'Sale'), ('Rent', 'Rent')], validators=[DataRequired()])
    bedrooms = IntegerField('Bedrooms', validators=[Optional(), NumberRange(min=0)])
    bathrooms = IntegerField('Bathrooms', validators=[Optional(), NumberRange(min=0)])
    area = IntegerField('Area (sq ft)', validators=[DataRequired(), NumberRange(min=1)])
    image = FileField('Property Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    amenities = TextAreaField('Amenities (Comma separated)', validators=[Optional()])
    submit = SubmitField('Save Property')

class InquiryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Inquiry')

