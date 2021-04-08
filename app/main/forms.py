from flask import request
from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class HiddenDirLocationForm(FlaskForm):
    dir_path = HiddenField()
    submit = SubmitField(u'Go')

class DirLocationForm(FlaskForm):
    dir_path = StringField(u'Path', validators=[DataRequired()])
    go = SubmitField(u'Go')

class AlbumInfoForm(FlaskForm):
    album_name = StringField(u'Album Name', validators=[DataRequired()])
    album_artist = StringField(u'Album Artist', validators=[DataRequired()])
    normalize_file_names = BooleanField(u'Strip Leading Song Number From File Names')
    submit = SubmitField(u'Apply to All Songs')

class SearchForm(FlaskForm):
    q = StringField(u'Search', validators=[DataRequired(), Length(min=3)])
    mixOnly = BooleanField(u'Search Only In Mixes', default=True)
    artists = BooleanField(u'Search Artists', default=False)

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)

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
    size = StringField(u'Size', render_kw={'readonly': True})
    length = StringField(u'Length', render_kw={'readonly': True})
    bitrate = StringField(u'Bitrate', render_kw={'readonly': True})
    samplerate = StringField(u'Sample Rate', render_kw={'readonly': True})
    bitspersample = StringField(u'Bits Per Sample', render_kw={'readonly': True})
    bpm = StringField(u'BPM', render_kw={'readonly': True})

    submit = SubmitField('Save Changes')
