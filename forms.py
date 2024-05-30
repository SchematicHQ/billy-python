from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms import Form
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
  search = StringField('search', validators=[DataRequired()])

class LoginForm(FlaskForm):
  username = StringField('username', validators=[DataRequired()])
  password = StringField('password', validators=[DataRequired()])