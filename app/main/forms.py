from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class DirLocationForm(FlaskForm):
    dir_path = StringField('Path', validators=[DataRequired()])
    submit = SubmitField('Enter')

class AlbumInfoForm(FlaskForm):
    album_name = StringField('Album Name', validators=[DataRequired()])
    album_artist = StringField('Album Artist', validators=[DataRequired()])
    submit = SubmitField('Save Changes')
