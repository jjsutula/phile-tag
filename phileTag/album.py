from .utils.fileio import FileIo
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

bp = Blueprint('album', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('album/index.html')


@bp.route('/files', methods=['GET', 'POST'])
def files():
    if request.method == 'POST':
        dir_path = request.form['dir_path']
        error = None

        if not dir_path:
            error = 'Directory Path is required.'

        if error is not None:
            flash(error)
        else:
            # return redirect(url_for('album.files'), dir_path)
            
            fileIo = FileIo
            dir = fileIo.readDir(dir_path)
            if 'error' in dir:
                flash(dir['error'])
            else:
            #    files = dir['audio_files']
                audio_files = []
                for filename in dir['audio_files']:
                    fl = {}
                    fl['name'] = filename
                    fl['title'] = 'Some Title'
                    fl['album'] = 'Some Album'
                    fl['artist'] = 'Some Artist'
                    fl['album_artist'] = 'Some Album Artist'
                    audio_files.append(fl)
                other_files = []
                for filename in dir['other_files']:
                    fl = {}
                    fl['name'] = filename
                    other_files.append(fl)

                albumMeta = {}
                albumMeta['album'] = 'Some Album'
                albumMeta['artist'] = 'Some Artist'
                albumMeta['album_artist'] = 'Some Album Artist'

                return render_template('album/files.html', audio_files=audio_files, other_files=other_files, albumMeta=albumMeta)

    return redirect(url_for('album.index'))

