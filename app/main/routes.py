import time
from app.utils.fileio import FileIo
from app.utils.metaSearcher import MetaSearcher
from app.utils.routeHelper import RouteHelper
from app.main.forms import (
    AlbumInfoForm, DirLocationForm, HiddenDirLocationForm, SearchForm, SongInfoForm
)
from flask import (
    flash, g, make_response, request, redirect, render_template, url_for, current_app, session
)
from operator import itemgetter
from werkzeug.exceptions import abort
from app.main import bp

# *******************************************************
# NOTE: For Icons, see https://icons.getbootstrap.com/
# *******************************************************

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
        sortdir['artist'] = 'asc'
        sortdir['file'] = 'asc'
        sortdir['title'] = 'asc'
        sortdir['track'] = 'asc'
        sortdir['size'] = 'asc'
        screensettings['sortdir'] = sortdir
        session['screensettings'] = screensettings
    return screensettings

def popFilenumToDetail():
    if 'filenumToDetail' in session:
        filenumToDetail = session['filenumToDetail']
        session.pop('filenumToDetail', None)
    else:
        filenumToDetail = -1
    return filenumToDetail

def pushFilenumToDetail(filenumToDetail):
    session['filenumToDetail'] = filenumToDetail

def compare_tracknumber(meta):
    return meta['tracknumber']

def compare_filename(meta):
    return meta['name'].lower()

def compare_title(meta):
    return meta['title'].lower()

def compare_artist(meta):
    return meta['artist'].lower()

def compare_album(meta):
    return meta['album'].lower()

def compare_size(meta):
    return meta['bytes']

# Render the file information to the screen
def renderFilesTemplate(fileIo, dir_path, dir):
    metaSearcher = MetaSearcher
    audio_files = []

    album_names = {}
    album_artists = {}

    audio_files_meta = metaSearcher.parseAlbum(dir_path, dir['audio_files'])
    meta_list = audio_files_meta['meta_list']
    filenumToDetail = popFilenumToDetail()
    count = 0
    total_seconds = 0
    for meta in meta_list:
        total_seconds += meta['length']
        if count == filenumToDetail:
            # Show detail for the requested file
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
                form.size.data = meta['byteStr']
                form.length.data = meta['lengthStr']
                form.bitrate.data = meta['bitrate']
                form.samplerate.data = meta['samplerate']
                form.bitspersample.data = meta['bitspersample']
                form.bpm.data = meta['bpm']
                meta['detail_form'] = form
        count += 1
    album_length = MetaSearcher.formatLength(round(total_seconds))

    other_files = []
    subdirs = []
    count = 0
    for filename in dir['subdirs']:
        fl = {}
        fl['name'] = filename
        fl['filenum'] = count
        count += 1
        subdirs.append(fl)
    count = 0
    for filename in dir['other_files']:
        fl = {}
        fl['name'] = filename
        fl['filenum'] = count
        count += 1
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
    elif screensettings['sorton'] == 'artist':
        reversesort = True if sortdir['artist'] == 'desc' else False
        meta_list.sort(key=compare_artist, reverse=reversesort)
    elif screensettings['sorton'] == 'size':
        reversesort = True if sortdir['size'] == 'desc' else False
        meta_list.sort(key=compare_size, reverse=reversesort)
    else:
        reversesort = True if sortdir['file'] == 'desc' else False
        if reversesort:
            meta_list.sort(key=compare_filename, reverse=True)

    search_form = SearchForm()
    search_form.mixOnly.data = True
    search_form.artists.data = False
    nav_form = DirLocationForm()
    nav_form.dir_path.data = dir_path
    basedir = current_app.config['BASE_DIR']
    if not basedir:
        basedir = ''
    num_songs = len(meta_list)
    resp = make_response(render_template('files.html', nav_form=nav_form, search_form=search_form, form=form, dir_path=dir_path, meta_list=meta_list, other_files=other_files, subdirs=subdirs, screensettings=screensettings, basedir=basedir, num_songs=num_songs, album_length=album_length))
    resp.set_cookie('dirPath', dir_path)
    routeHelper = RouteHelper
    routeHelper.putDirHistory(dir_path)

    return resp

def renderSearchTemplate(dir_path, basedir, search_list, mixOnly, artists):
    start = time.time() * 1000
    results = MetaSearcher.search(basedir, dir_path, search_list, mixOnly, artists)
    end = time.time() * 1000
    millis = int(end - start)
    if millis > 1000:
        seconds = int(millis / 1000)
        millis -= seconds * 1000
        print("Time elapsed = "+str(seconds)+"s, "+str(millis)+"ms")
    else:
        print("Time elapsed = "+str(millis)+"ms")
    if results['errors']:
        print('There were '+str(len(results['errors']))+' errors.')
        print(results['errors'])
    search_form = SearchForm()
    search_form.mixOnly.data = True
    search_form.artists.data = False
    nav_form = DirLocationForm()
    nav_form.dir_path.data = dir_path
    albums = list(results['albums'].values())
    albums = sorted(albums, key=lambda x: (x['album'].lower(), x['dir'].lower()))

    songs = results['songs']
    songs = sorted(songs, key=lambda x: (x['title'].lower(), x['album'].lower(), x['artist'].lower(), x['dir'].lower()))
    for album in albums:
        hiddenDirLocationForm = HiddenDirLocationForm()
        hiddenDirLocationForm.dir_path.data = album['dir']
        hiddenDirLocationForm.submit.label.text = album['dir']
        album['form'] = hiddenDirLocationForm
    for song in songs:
        hiddenDirLocationForm = HiddenDirLocationForm()
        hiddenDirLocationForm.dir_path.data = song['dir']
        hiddenDirLocationForm.submit.label.text = song['dir']
        song['form'] = hiddenDirLocationForm
    if len(search_list) == 1:
        search_text = search_list[0]
    else:
        search_text = 'Matching mix songs in '+dir_path
    return render_template('search.html', title='Search', nav_form=nav_form, search_form=search_form,
                    albums=albums, songs=songs, search_text=search_text, artists=artists)

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
    nav_form = DirLocationForm()
    if dir_path:
        nav_form.dir_path.data = dir_path
    search_form = SearchForm()
    search_form.mixOnly.data = True
    search_form.artists.data = False
    return render_template('index.html', nav_form=nav_form, search_form=search_form, form=form)


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


@bp.route('/albuminfo', methods=['POST'])
def album_info():
    dir_path = request.cookies.get('dirPath')
    form = AlbumInfoForm()
    if form.validate_on_submit():
        metaSearcher = MetaSearcher        
        message = metaSearcher.changeAlbumInfo(dir_path, form.album_name.data, form.album_artist.data, form.normalize_file_names.data)
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
            if filenum.isnumeric():
                filenumber = int(filenum)
                pushFilenumToDetail(filenumber)
        return redirect(url_for('main.files'))
    return redirect(url_for('main.index'))


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
                for file_info in audio_files:
                    filename = file_info['filename']
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
    if sorton in ['artist','file','size','title','track']:
        if screensettings['sorton'] == sorton:
            # Flip the sort direction if they clicked the column that is currently sorted
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


@bp.route('/cd/<filenum>', methods=['GET'])
def change_dir(filenum):
    dir_path = request.cookies.get('dirPath')
    if dir_path:
        fileIo = FileIo
        dir = fileIo.readDir(dir_path)
        if 'error' in dir:
            flash(dir['error'])
            return redirect(url_for('main.index'))
        else:
            if filenum.isnumeric():
                filenumber = int(filenum)
                subdirs = dir['subdirs']
                if len(subdirs) >= filenumber:
                    new_dir_path = dir_path + '/' + subdirs[filenumber]
            elif filenum == 'back':
                routeHelper = RouteHelper
                new_dir_path = routeHelper.getPreviousDir(dir_path)
            elif filenum == 'next':
                routeHelper = RouteHelper
                new_dir_path = routeHelper.getNextDir(dir_path)
            elif filenum == 'up':
                routeHelper = RouteHelper
                new_dir_path = routeHelper.getParentDir(dir_path)
            elif filenum == 'base':
                basedir = current_app.config['BASE_DIR']
                if not basedir:
                    basedirs = ''
                new_dir_path = basedir
            else:
                return redirect(url_for('main.files'))

            if new_dir_path:
                dir = fileIo.readDir(new_dir_path)
                if 'error' in dir:
                    flash(dir['error'])
                    return redirect(url_for('main.index'))
                else:
                    resp = make_response(redirect(url_for('main.files')))
                    resp.set_cookie('dirPath', new_dir_path)
                    return resp

    return redirect(url_for('main.files'))


@bp.route('/search', methods=['GET'])
def search():
    if 'q' in request.args:
        search_text = request.args['q']
        if ('mixOnly' in request.args and request.args['mixOnly'] == 'y'):
            mixOnly = True
        else:
            mixOnly = False
        if ('artists' in request.args and request.args['artists'] == 'y'):
            artists = True
        else:
            artists = False
        if len(search_text) < 3:
            if len(search_text) > 0:
                flash("Search text must be at least 3 characters.")
        else:
            dir_path = request.cookies.get('dirPath')
            basedir = current_app.config['BASE_DIR']
            if not basedir:
                flash('No BASE_DIR parameter is configured in the configuration properties. Searching from current directory instead.')
                basedir = dir_path
            return renderSearchTemplate(dir_path, basedir, [search_text], mixOnly, artists)
    return redirect(url_for('main.files'))


@bp.route('/duplicates', methods=['GET'])
def duplicates():
    dir_path = request.cookies.get('dirPath')
    fileIo = FileIo
    dir = fileIo.readDir(dir_path)
    if 'error' in dir:
        flash(dir['error'])
        return redirect(url_for('main.index'))
    
    albums = {}
    search_list = []
    metaSearcher = MetaSearcher
    audio_files_meta = metaSearcher.parseAlbum(dir_path, dir['audio_files'])
    meta_list = audio_files_meta['meta_list']
    for meta in meta_list:
        if meta['album'] not in albums:
            albums[meta['album']] = True
            search_list.append(meta['album'])
        search_list.append(meta['title'])
    basedir = current_app.config['BASE_DIR']
    if not basedir:
        flash('No BASE_DIR parameter is configured in the configuration properties. Cannot search for duplicates.')
        return redirect(url_for('main.index'))
    return renderSearchTemplate(dir_path, basedir, search_list, True, False)


@bp.route('/navdir', methods=['POST'])
def navdir():
    dir_path = request.cookies.get('dirPath')
    hiddenDirLocationForm = HiddenDirLocationForm()
    if hiddenDirLocationForm.validate_on_submit():
        message = hiddenDirLocationForm.dir_path.data
        if message != '':
            dir_path = message
    resp = make_response(redirect(url_for('main.files')))
    resp.set_cookie('dirPath', dir_path)
    return resp