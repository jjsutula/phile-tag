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
            files = fileIo.readDir(dir_path)

            albumMeta = {}
            albumMeta['album'] = 'Some Album'
            albumMeta['artist'] = 'Some Artist'
            albumMeta['album_artist'] = 'Some Album Artist'

            return render_template('album/files.html', files=files, albumMeta=albumMeta)

    return redirect(url_for('album.index'))

