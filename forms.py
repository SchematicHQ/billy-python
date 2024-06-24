from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms import Form
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    search = StringField(
        "",
        validators=[DataRequired()],
        render_kw={"placeholder": "Search billy for images..."},
    )


class LoginForm(FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    password = StringField("password", validators=[DataRequired()])
