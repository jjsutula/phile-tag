from app.utils.fileio import FileIo
from app.utils.metaSearcher import MetaSearcher
from app.main.forms import AlbumInfoForm
from app.main.forms import DirLocationForm
from app.main.forms import SongInfoForm
from flask import (
    flash, g, make_response, request, redirect, render_template, url_for, current_app, session
)
from werkzeug.exceptions import abort
from app.main import bp

# *******************************************************
# *** Helpers
# *******************************************************

# Retrieve the screen settings from the session
def getScreensettings():
    if 'screensettings' in session:
        screensettings = session['screensettings']
    else:
        # Initialize and insert to session
        screensettings = {}
        screensettings['showarrows'] = False
        screensettings['arrowcolor'] = 'black'
        screensettings['sorton'] = 'track'
        sortdir = {}
        sortdir['file'] = 'asc'
        sortdir['title'] = 'asc'
        sortdir['track'] = 'asc'
        screensettings['sortdir'] = sortdir
        session['screensettings'] = screensettings
    return screensettings

def compare_tracknumber(meta):
    return meta['tracknumber']

def compare_filename(meta):
    return meta['name']

def compare_title(meta):
    return meta['title']

# Render the file information to the screen
def renderFilesTemplate(fileIo, dir_path, dir, filenumToDetail):
    metaSearcher = MetaSearcher
    audio_files = []

    album_names = {}
    album_artists = {}

    audio_files_meta = metaSearcher.parseAlbum(dir_path, dir['audio_files'])
    meta_list = audio_files_meta['meta_list']
    if filenumToDetail > -1:
        # Show detail for the requested file
        count = 0
        for meta in meta_list:
            if count == filenumToDetail:
                if 'detail_form' in meta:
                    # Detail was showing, now remove the form to quit showing
                    meta.pop('detail_form', None)
                else:
                    form = SongInfoForm()
                    form.title.data = meta['title']
                    form.artist.data = meta['artist']
                    form.album.data = meta['album']
                    form.tracknumber.data = meta['tracknumber']
                    form.albumartist.data = meta['albumartist']
                    form.filename.data = meta['name']
                    form.originalFilename.data = meta['name']
                    form.genre.data = meta['genre']
                    form.date.data = meta['date']
                    form.length.data = meta['length']
                    form.bitrate.data = meta['bitrate']
                    form.samplerate.data = meta['samplerate']
                    form.bitspersample.data = meta['bitspersample']
                    form.bpm.data = meta['bpm']
                    meta['detail_form'] = form
            count += 1

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

    screensettings = getScreensettings()
    sortdir = screensettings['sortdir']
    if screensettings['sorton'] == 'track':
        reversesort = True if sortdir['track'] == 'desc' else False
        meta_list.sort(key=compare_tracknumber, reverse=reversesort)
    elif screensettings['sorton'] == 'title':
        reversesort = True if sortdir['title'] == 'desc' else False
        meta_list.sort(key=compare_title, reverse=reversesort)
    else:
        reversesort = True if sortdir['file'] == 'desc' else False
        if reversesort:
            meta_list.sort(key=compare_filename, reverse=True)

    resp = make_response(render_template('files.html', form=form, meta_list=meta_list, other_files=other_files, subdirs=subdirs, screensettings=screensettings))
    resp.set_cookie('dirPath', dir_path)

    return resp

# *******************************************************
# *** ROUTES
# *******************************************************
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
                return renderFilesTemplate(fileIo, dir_path, dir, -1)

    dir_path = request.cookies.get('dirPath')
    if dir_path:
        fileIo = FileIo
        dir = fileIo.readDir(dir_path)
        if 'error' in dir:
            flash(dir['error'])
            return redirect(url_for('main.index'))
        else:
            return renderFilesTemplate(fileIo, dir_path, dir, -1)
    else:
        return redirect(url_for('main.index'))


@bp.route('/albuminfo', methods=['POST'])
def album_info():
    dir_path = request.cookies.get('dirPath')
    form = AlbumInfoForm()
    if form.validate_on_submit():
        metaSearcher = MetaSearcher        
        message = metaSearcher.changeAlbumInfo(dir_path, form.album_name.data, form.album_artist.data)
        if message != '':
            flash(message)
    return redirect(url_for('main.files'))


@bp.route('/songinfo/<filenum>', methods=['GET','POST'])
def song_info(filenum):
    dir_path = request.cookies.get('dirPath')
    if dir_path:
        fileIo = FileIo
        dir = fileIo.readDir(dir_path)
        if 'error' in dir:
            flash(dir['error'])
            return redirect(url_for('main.index'))
        else:
            audio_files = dir['audio_files']
            if filenum.isnumeric():
                filenumber = int(filenum)
            else:
                return redirect(url_for('main.files'))

            return renderFilesTemplate(fileIo, dir_path, dir, filenumber)

@bp.route('/songupdate', methods=['POST'])
def song_update():
    dir_path = request.cookies.get('dirPath')
    songInfoForm = SongInfoForm()
    if songInfoForm.validate_on_submit():
        metaSearcher = MetaSearcher
        message = metaSearcher.writeSongDetails(dir_path, songInfoForm)
        if message != '':
            flash(message)
    return redirect(url_for('main.files'))

@bp.route('/togglearrows', methods=['GET'])
def togglearrows():
    screensettings = getScreensettings()
    screensettings['showarrows'] = not screensettings['showarrows']
    if screensettings['showarrows']:
        screensettings['arrowcolor'] = 'gray'
        # The arrows are showing so the sort must be on 'track'
        screensettings['sorton'] = 'track'
    else:
        screensettings['arrowcolor'] = 'black'
    session['screensettings'] = screensettings
    return redirect(url_for('main.files'))

@bp.route('/track/<arrow>/<filenumToChange>', methods=['GET'])
def track(arrow, filenumToChange):
    dir_path = request.cookies.get('dirPath')
    if dir_path:
        fileIo = FileIo
        dir = fileIo.readDir(dir_path)
        if 'error' in dir:
            flash(dir['error'])
            return redirect(url_for('main.index'))
        else:
            audio_files = dir['audio_files']
            if filenumToChange.isnumeric():
                filenumber = int(filenumToChange)
                count = 0
                for filename in audio_files:
                    if count == filenumber:
                        metaSearcher = MetaSearcher
                        screensettings = getScreensettings()
                        sort = screensettings['sortdir']['track']
                        if (arrow == 'up' and sort == 'asc') or (arrow == 'down' and sort == 'desc'):
                            direction = 'lower'
                        else:
                            direction = 'higher'
                        metaSearcher.changeTrackNumber(dir_path, filename, direction)
                        break
                    count += 1

    return redirect(url_for('main.files'))

@bp.route('/sort/<sorton>/<currentsortdir>', methods=['GET'])
def sort(sorton, currentsortdir):
    screensettings = getScreensettings()
    if sorton in ['file','title','track']:
        if screensettings['sorton'] == sorton:
            # Flip the sort diection if they clicked the column that is currently sorted
            sortdir = 'asc' if currentsortdir == 'desc' else 'desc'
        else:
            # Do not flip it if they clicked on a different column, instead sort by the last sorted value
            screensettings['sorton'] = sorton
            sortdir = 'asc' if currentsortdir == 'asc' else 'desc'
        screensortdir = screensettings['sortdir']
        screensortdir[sorton] = sortdir
        if sorton != 'track':
            # Do not show the arrows when not sorting on 'Track'
            screensettings['showarrows'] = False
            screensettings['arrowcolor'] = 'black'
        session['screensettings'] = screensettings
    return redirect(url_for('main.files'))
