from app.utils.fileio import FileIo
from app.main.forms import DirLocationForm
from flask import (
    flash, g, redirect, render_template, url_for, current_app
)
from werkzeug.exceptions import abort
from app.main import bp


@bp.route('/', methods=['GET', 'POST'])
def index():
    # # An example of how to acces the configuration keys
    # (current_app is only accessible during the handling of a request):
    # print('key='+current_app.config['SECRET_KEY'])
    #  If starting a thread and that thread will need current_app, do it like this:
        # Thread(target=send_async_email,
        #    args=(current_app._get_current_object(), msg)).start()

    form = DirLocationForm()
    return render_template('index.html', form=form)


@bp.route('/files', methods=['GET', 'POST'])
def files():
    form = DirLocationForm()
    if form.validate_on_submit():
        dir_path = form.dir_path.data
        error = None

        if not dir_path:
            error = 'Directory Path is required.'

        if error is not None:
            flash(error)
        else:
            
            fileIo = FileIo
            dir = fileIo.readDir(dir_path)
            if 'error' in dir:
                flash(dir['error'])
            else:
            #    files = dir['audio_files']
                audio_files = []
                for filename in dir['audio_files']:
                    if (filename.endswith('.flac')):
                        fl = fileIo.parseFlac(dir_path, filename)
                    elif (filename.endswith('.mp3')):
                        fl = fileIo.parseMp3(dir_path, filename)
                    # fl = {}
                    # fl['name'] = filename
                    # fl['title'] = 'Some Title'
                    # fl['album'] = 'Some Album'
                    # fl['artist'] = 'Some Artist'
                    # fl['album_artist'] = 'Some Album Artist'
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

                return render_template('files.html', audio_files=audio_files, other_files=other_files, albumMeta=albumMeta)

    return render_template('index.html', form=form)
