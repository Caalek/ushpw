from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import URL, DataRequired, Length

class RandomShorten(FlaskForm):
    long_url = StringField()
    submit_random = SubmitField('Shorten')

class CustomShorten(FlaskForm):
    url = StringField()
    text = StringField()
    submit_custom = SubmitField('Create a Custom URL')

class ClickCounter(FlaskForm):
    short_url = StringField()
    submit_counter = SubmitField('Get Amount of Clicks')

