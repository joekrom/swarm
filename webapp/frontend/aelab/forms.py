from flask_wtf import FlaskForm
from wtforms import Form, StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, FloatField, FormField
from wtforms.fields.html5 import EmailField, DateField, TimeField
from wtforms.validators import DataRequired , Length , EqualTo, Email

class RegistrationForm(FlaskForm):
    email = EmailField('@email:',validators=[DataRequired(),Email()])
    username = StringField('Username:',validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired(),EqualTo('confirm', message='password must match')])
    confirm = PasswordField('Repeat password:')
    student_id = StringField('student_id:', validators=[DataRequired()])
    submit = SubmitField('Sign up')

class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    submit = SubmitField('Sign in')

class DroneForm(FlaskForm):
    serial_number = StringField('serial number',validators=[DataRequired()])
    name = StringField('name',validators=[DataRequired()])
    type = StringField('type of drone',validators=[DataRequired()])
    flight_time = IntegerField('flight time in min ',validators=[DataRequired()])
    weight=IntegerField('weight in gramme',validators=[DataRequired()])
    span=IntegerField('span in meter',validators=[DataRequired()])
    radius=IntegerField('radius in meter',validators=[DataRequired()])
    max_altitude=IntegerField('max height in meter',validators=[DataRequired()])
    submit = SubmitField('add drone')

class AccreditationForm(FlaskForm):
    date = DateField('',validators=[DataRequired()])
    hour = TimeField('',validators=[DataRequired()])
    duration = IntegerField('',validators=[DataRequired()])
    type = SelectField('drones',choices=[],validators=[DataRequired()])
    altitude = IntegerField('',validators=[DataRequired()])
    radius = IntegerField('',validators=[DataRequired()])
    submit = SubmitField('send request')


#class for the mission form
class ArmningForm(FlaskForm):
    credential = StringField('credential',validators=[DataRequired()])
    arm = SubmitField('arm')

class TakeoffForm(FlaskForm):
    alt = IntegerField('alt',validators=[DataRequired()])
    credential = StringField('credential',validators=[DataRequired()])
    takeoff = SubmitField('takeoff')

class GotoForm(FlaskForm):
    alt = IntegerField('alt',validators=[DataRequired()])
    lat = IntegerField('lat',validators=[DataRequired()])
    long = IntegerField('long',validators=[DataRequired()])
    credential = StringField('credential',validators=[DataRequired()])
    goto = SubmitField('goto')
