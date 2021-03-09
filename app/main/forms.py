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

class SongInfoForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    artist = StringField('Artist', validators=[DataRequired()])
    album = StringField('Album', validators=[DataRequired()])
    tracknumber = StringField('Track', validators=[DataRequired()])
    albumartist = StringField('Album Artist', validators=[DataRequired()])
    filename = StringField('File Name', validators=[DataRequired()])
    genre = StringField('Genre')
    date = StringField('Date')
    length = StringField('Length', render_kw={'readonly': True})
    bitrate = StringField('Bitrate', render_kw={'readonly': True})
    samplerate = StringField('Sample Rate', render_kw={'readonly': True})
    bitspersample = StringField('Bits Per Sample', render_kw={'readonly': True})
    bpm = StringField('BPM', render_kw={'readonly': True})

    submit = SubmitField('Save Changes')
