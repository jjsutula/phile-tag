from app.utils.fileio import FileIo
from app.utils.metaSearcher import MetaSearcher
from app.main.forms import AlbumInfoForm
from app.main.forms import DirLocationForm
from flask import (
    flash, g, make_response, request, redirect, render_template, url_for, current_app
)
from werkzeug.exceptions import abort
from app.main import bp

# Update the album information common to all files in the folder
def changeAlbumInfo(album_info, album_artist):
    print('New album_info:'+album_info+', New Album Artist: '+album_artist)

# Render the file information to the screen
def renderFilesTemplate(fileIo, dir_path, dir):
    metaSearcher = MetaSearcher
    audio_files = []

    album_names = {}
    album_artists = {}

    audio_files_meta = metaSearcher.parseAlbum(dir_path, dir['audio_files'])
    meta_list = audio_files_meta['meta_list']
    other_files = []
    subdirs = []
    for filename in dir['subdirs']:
        fl = {}
        fl['name'] = filename
        subdirs.append(fl)
    for filename in dir['other_files']:
        fl = {}
        fl['name'] = filename
        other_files.append(fl)

    form = AlbumInfoForm()
    form.album_artist.data = audio_files_meta['album_artist']
    form.album_name.data = audio_files_meta['album_name']
    resp = make_response(render_template('files.html', form=form, meta_list=meta_list, other_files=other_files, subdirs=subdirs))
    resp.set_cookie('dirPath', dir_path)
    return resp


@bp.route('/', methods=['GET', 'POST'])
def index():
    # # An example of how to access the configuration keys
    # (current_app is only accessible during the handling of a request):
    # print('key='+current_app.config['SECRET_KEY'])
    #  If starting a thread and that thread will need current_app, do it like this:
        # Thread(target=send_async_email,
        #    args=(current_app._get_current_object(), msg)).start()

    dir_path = request.cookies.get('dirPath')
    form = DirLocationForm()
    if dir_path:
        form.dir_path.data = dir_path
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
                return redirect(url_for('main.index'))
            else:
                return renderFilesTemplate(fileIo, dir_path, dir)

    dir_path = request.cookies.get('dirPath')
    if dir_path:
        fileIo = FileIo
        dir = fileIo.readDir(dir_path)
        if 'error' in dir:
            flash(dir['error'])
            return redirect(url_for('main.index'))
        else:
            return renderFilesTemplate(fileIo, dir_path, dir)
    else:
        return redirect(url_for('main.index'))


@bp.route('/albuminfo', methods=['GET', 'POST'])
def album_info():
    dir_path = request.cookies.get('dirPath')
    form = AlbumInfoForm()
    if form.validate_on_submit():
        changeAlbumInfo(form.album_name.data, form.album_artist.data)
        flash('Your changes have been saved.')
    # elif request.method == 'GET':
    #     form.album_artist.data = 'jonnynono-x'
    #     form.album_name.data = 'whatever, dude'

    if dir_path:
        fileIo = FileIo
        dir = fileIo.readDir(dir_path)
        if 'error' in dir:
            flash(dir['error'])
            return redirect(url_for('main.index'))
        else:
            return renderFilesTemplate(fileIo, dir_path, dir)
    else:
        return redirect(url_for('main.index'))
