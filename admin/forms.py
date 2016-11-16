from flask_wtf import Form
from wtforms import StringField, TextAreaField, SubmitField, SelectField,\
    BooleanField
from wtforms.validators import DataRequired, Length, Regexp, Email
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField
from ..models import User, Role


class EntryForm(Form):
    title = StringField('Title:', validators=[DataRequired()])
    body = PageDownField('Content:', validators=[DataRequired()])
    submit = SubmitField('Publish')


class TagForm(Form):
    name = StringField('Tag', validators=[DataRequired()])
    submit = SubmitField('+Tag')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    name = StringField('Name', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Names must have only letters, '
                                              'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')