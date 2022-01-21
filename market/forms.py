from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from werkzeug.utils import secure_filename
from market.models import User

class RegisterForm(FlaskForm):

    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists.')

    def validate_email_address(self, email_address_to_check):
        user = User.query.filter_by(email_address=email_address_to_check.data).first()
        if user:
            raise ValidationError('An account already exists for this email address.')

    username = StringField(label='Username', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email Address', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Choose a password', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm password', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create account')

class LoginForm(FlaskForm):

    username = StringField(label='Username', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')

class CreateForm(FlaskForm):

    name = StringField(label='Name', validators=[Length(min=2, max=30), DataRequired()])
    price = IntegerField(label='Price', validators=[DataRequired()])
    description = StringField(label='Description', validators=[Length(min=2, max=1024), DataRequired()])
    file = FileField()
    submit = SubmitField(label='Create product')

class UpdateForm(FlaskForm):

    name = StringField(label='Name', validators=[Length(min=2, max=30), DataRequired()])
    price = IntegerField(label='Price', validators=[DataRequired()])
    description = StringField(label='Description', validators=[Length(min=2, max=1024), DataRequired()])
    submit = SubmitField(label='Update listing')

class DeleteForam(FlaskForm):

    submit = SubmitField(label='Delete this item')

class BuyForm(FlaskForm):

    submit = SubmitField(label='Buy now')

class SellForm(FlaskForm):

    name = StringField(label='Name', validators=[Length(min=2, max=30), DataRequired()])
    price = IntegerField(label='Price', validators=[DataRequired()])
    description = StringField(label='Description', validators=[Length(min=2, max=1024), DataRequired()])
    submit = SubmitField(label='List this item')

class UnlistForm(FlaskForm):

    submit = SubmitField(label='Unlist this item')
