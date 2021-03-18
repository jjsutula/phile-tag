from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired


class DirLocationForm(FlaskForm):
    dir_path = StringField(u'Path', validators=[DataRequired()])
    go = SubmitField(u'Go')

class AlbumInfoForm(FlaskForm):
    album_name = StringField(u'Album Name', validators=[DataRequired()])
    album_artist = StringField(u'Album Artist', validators=[DataRequired()])
    submit = SubmitField(u'Apply to All Songs')

class SongInfoForm(FlaskForm):
    title = StringField(u'Title', validators=[DataRequired()])
    artist = StringField(u'Artist', validators=[DataRequired()])
    album = StringField(u'Album', validators=[DataRequired()])
    tracknumber = StringField(u'Track', validators=[DataRequired()])
    albumartist = StringField(u'Album Artist', validators=[DataRequired()])
    filename = StringField(u'File Name', validators=[DataRequired()])
    originalFilename = HiddenField(u'File Name')
    genre = StringField(u'Genre', validators=[DataRequired()])
    date = StringField(u'Date')
    length = StringField(u'Length', render_kw={'readonly': True})
    bitrate = StringField(u'Bitrate', render_kw={'readonly': True})
    samplerate = StringField(u'Sample Rate', render_kw={'readonly': True})
    bitspersample = StringField(u'Bits Per Sample', render_kw={'readonly': True})
    bpm = StringField(u'BPM', render_kw={'readonly': True})

    submit = SubmitField('Save Changes')
