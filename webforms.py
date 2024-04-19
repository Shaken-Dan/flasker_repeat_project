from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo
from wtforms.widgets.core import TextArea


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create Blog Post Form
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    author = StringField('Author', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    submit = SubmitField('Submit')


class PasswordForm(FlaskForm):
    email = StringField('What is your email?', validators=[DataRequired()])
    password_hash = PasswordField('What is your password?', validators=[DataRequired()])
    submit = SubmitField('Submit')


# Create a form class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    password_hash = PasswordField("Password", validators=[DataRequired(),
                                                          EqualTo("password_hash2", message="Passwords must match")])
    password_hash2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField('Submit')





