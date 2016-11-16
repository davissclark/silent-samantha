from flask.ext.wtf import Form
from wtforms import SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class SubscribeForm(Form):
    email = EmailField('Email', validators=[DataRequired()])
    submit = SubmitField('Subscribe')