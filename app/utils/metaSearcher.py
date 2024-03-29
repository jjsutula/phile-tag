import os, string
from app.utils.fileio import FileIo
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

# NOTE: See https://code.google.com/archive/p/mutagen/wikis/Tutorial.wiki

class MetaSearcher:

    # This mechanism has been benchmarked to be much faster than using regex
    # Makes a string consisting of everything but upper, lower alpha chars and numbers,
    # then converts that string to a table
    translation_table = str.maketrans('', '', ''.join(c for c in map(chr, range(128)) if not c.isalnum()))

    # ****************
    # Internal helper methods
    # ****************
    def _invokeEasyID3(path):
        try:
            audio = EasyID3(path)
        except Exception as ex:
            audio = None
            print("An error occurred attempting to extract ID3 information from '"+path+"'. Error was " + str(ex))
        return audio

    def _invokeFLAC(path):
        try:
            audio = FLAC(path)
        except Exception as ex:
            audio = None
            print("An error occurred attempting to extract FLAC information from '"+path+"'. Error was " + str(ex))
        return audio

    def formatLength(numSeconds):
        hours = 0
        minutes = 0
        retval = ''
        if (numSeconds >= 3600):
            hours = int(numSeconds / 3600)
            numSeconds = numSeconds - (hours * 3600)
            retval = str(hours) + 'h '
        if (numSeconds >= 60):
            minutes = int(numSeconds / 60)
            numSeconds = numSeconds - (minutes * 60)
            retval = retval + str(minutes) + 'm '
        return retval + str(numSeconds) + 's'

    def formatSize(numBytes):
        if numBytes < 1024:
            return str(numBytes)+' B'
        if numBytes < 1024*1024:
            kb = numBytes / 1024
            return '{:.1f}'.format(kb)+' kB'
        mb = numBytes / (1024*1024)
        return '{:.1f}'.format(mb)+' MB'

    def remove_text_in_parens(text):
        retval = ''
        skip = 0
        for ch in text:
            if ch == '(':
                skip += 1
            elif ch == ')':
                skip -= 1
            elif skip < 1:
                retval += ch
        return retval

    def prepareTextForCompare(text):
        if text:
            # Ignore text between parens
            text = MetaSearcher.remove_text_in_parens(text)
            if text:
                # Removes al non alphanumerics
                text = text.lower().translate(MetaSearcher.translation_table)
            else:
                text = ' '
        return text

    def convertToNum(value):
        if value.isnumeric():
            return int(value)
        return 0

    def getEasyId3Text(audio, key):
        if audio is None:
            if key == 'artist':
                return '<Invalid MP3 Format>'
        elif key in audio:
            return audio[key][0]
        return ''

    # def getId3Text(audio, key):
    #     if key in audio:
    #         return audio[key].text[0]
    #     return ''

    def extractDirName(dir_path):
        last_ndx = dir_path.rfind(os.path.sep)
        return dir_path[last_ndx+1:]

    def setEasyId3Text(audio, key, text):
        changed = False
        if audio and text:
            if key not in audio or audio[key][0] != text:
                audio[key] = text
                changed = True
        return changed

    def searchEasyId3(dir_path, search_results, compressed_search_text, audio, artists, is_duplicate_search):
        ndx = -1
        if artists:
            artist = MetaSearcher.getEasyId3Text(audio, 'artist')
            artist_scrunched = MetaSearcher.prepareTextForCompare(artist)
            if is_duplicate_search:
                if artist_scrunched == compressed_search_text:
                    ndx = 0
            else:
                ndx = artist_scrunched.find(compressed_search_text)
            if ndx > -1:
                title = MetaSearcher.getEasyId3Text(audio, 'title')
                album = MetaSearcher.getEasyId3Text(audio, 'album')
                song_info = {}
                song_info['album'] = album
                song_info['artist'] = artist
                song_info['title'] = title
                song_info['dir'] = dir_path
                search_results['songs'].append(song_info)

                # Now tag the album as well
                key = dir_path + ':' + album
                if key not in search_results['albums']:
                    album_info = {}
                    album_info['album'] = album
                    album_info['dir'] = dir_path
                    search_results['albums'][key] = album_info
        else:
            album = MetaSearcher.getEasyId3Text(audio, 'album')
            album_scrunched = MetaSearcher.prepareTextForCompare(album)
            if is_duplicate_search:
                if album_scrunched == compressed_search_text:
                    ndx = 0
            else:
                ndx = album_scrunched.find(compressed_search_text)
            if ndx > -1:
                # Album found, put it in the result only if not already there
                key = dir_path + ':' + album
                if key not in search_results['albums']:
                    album_info = {}
                    album_info['album'] = album
                    album_info['dir'] = dir_path
                    search_results['albums'][key] = album_info

            title = MetaSearcher.getEasyId3Text(audio, 'title')
            title_scrunched = MetaSearcher.prepareTextForCompare(title)
            if is_duplicate_search:
                if title_scrunched == compressed_search_text:
                    ndx = 0
            else:
                ndx = title_scrunched.find(compressed_search_text)
            if ndx > -1:
                # Song found, always put it in the result
                artist = MetaSearcher.getFlacText(audio, 'artist')
                song_info = {}
                song_info['album'] = album
                song_info['artist'] = artist
                song_info['title'] = title
                song_info['dir'] = dir_path
                search_results['songs'].append(song_info)

    def getFlacText(audio, key):
        if audio is None:
            if key == 'artist':
                return '<Invalid FLAC Format>'
        elif key in audio:
            return audio[key][0]
        return ''

    def setFlacText(audio, key, text):
        changed = False
        if text and audio:
            if key not in audio or audio[key][0] != text:
                audio[key] = text
                changed = True
        return changed

    def searchFlac(dir_path, search_results, compressed_search_text, audio, artists, is_duplicate_search):
        ndx = -1
        if artists:
            artist = MetaSearcher.getFlacText(audio, 'artist')
            artist_scrunched = MetaSearcher.prepareTextForCompare(artist)
            if is_duplicate_search:
                if artist_scrunched == compressed_search_text:
                    ndx = 0
            else:
                ndx = artist_scrunched.find(compressed_search_text)
            if ndx > -1:
                title = MetaSearcher.getFlacText(audio, 'title')
                album = MetaSearcher.getFlacText(audio, 'album')
                song_info = {}
                song_info['album'] = album
                song_info['artist'] = artist
                song_info['title'] = title
                song_info['dir'] = dir_path
                search_results['songs'].append(song_info)

                # Now tag the album as well
                key = dir_path + ':' + album
                if key not in search_results['albums']:
                    album_info = {}
                    album_info['album'] = album
                    album_info['dir'] = dir_path
                    search_results['albums'][key] = album_info
        else:
            album = MetaSearcher.getFlacText(audio, 'album')
            album_scrunched = MetaSearcher.prepareTextForCompare(album)
            if is_duplicate_search:
                if album_scrunched == compressed_search_text:
                    ndx = 0
            else:
                ndx = album_scrunched.find(compressed_search_text)
            if ndx > -1:
                # Album found, put it in the result only if not already there
                key = dir_path + ':' + album
                if key not in search_results['albums']:
                    album_info = {}
                    album_info['album'] = album
                    album_info['dir'] = dir_path
                    search_results['albums'][key] = album_info

            title = MetaSearcher.getFlacText(audio, 'title')
            title_scrunched = MetaSearcher.prepareTextForCompare(title)
            if is_duplicate_search:
                if title_scrunched == compressed_search_text:
                    ndx = 0
            else:
                ndx = title_scrunched.find(compressed_search_text)
            if ndx > -1:
                # Song found, always put it in the result
                artist = MetaSearcher.getFlacText(audio, 'artist')
                song_info = {}
                song_info['album'] = album
                song_info['artist'] = artist
                song_info['title'] = title
                song_info['dir'] = dir_path
                search_results['songs'].append(song_info)

    # This is used for verifying that all tracks are sequential and accounted for.
    # The return value reflects whether there is a problem with the track number
    def compileTrackList(tracks_found, meta):
        track_num = meta['tracknumber']
        if track_num < 1 or track_num > 1000:
            # Invalid track number so stick it in the '0' bucket
            if len(tracks_found) == 0:
                tracks_found.append([])
            tracks_found[0].append(meta)
        else:    
            if len(tracks_found) < track_num + 1:
                for n in range(len(tracks_found), track_num + 1):
                    tracks_found.append([])
            tracks_found[track_num].append(meta)

    def verifyTracksAreSequential(tracks_found):
        skipped = False
        for track_num in range(len(tracks_found)):
            meta_list = tracks_found[track_num]
            if track_num == 0:
                for meta in meta_list:
                    if 'different' not in meta:
                        meta['different'] = {}
                    meta['different']['track'] = True
            else:
                if len(meta_list) == 0:
                    skipped = True
                elif skipped or len(meta_list) > 1:
                    # Either tracks were skipped or duplicates were found
                    skipped = False
                    for meta in meta_list:
                        if 'different' not in meta:
                            meta['different'] = {}
                        meta['different']['track'] = True

    # ****************
    # Public methods
    # ****************

    #   Returns:
    #     meta
    #       name
    #       title
    #       album
    #       albumartist
    #       artist
    #       tracknumber
    #       genre
    #       date
    #       length
    #       bitrate
    #       samplerate
    #       bitspersample (flac)
    #       bpm (flac)
    #       is_compilation *
    #       notes *
    def parseFlac(dir_path, filename):
        meta = {}
        meta['name'] = filename
        audio = MetaSearcher._invokeFLAC(dir_path + '/' + filename)
        title = MetaSearcher.getFlacText(audio, 'title')
        if not title:
            title = '<untitled>'
        meta['title'] = title
        meta['album'] = MetaSearcher.getFlacText(audio, 'album')
        meta['albumartist'] = MetaSearcher.getFlacText(audio, 'albumartist')
        meta['artist'] = MetaSearcher.getFlacText(audio, 'artist')
        meta['tracknumber'] = MetaSearcher.convertToNum(MetaSearcher.getFlacText(audio, 'tracknumber'))
        meta['genre'] = MetaSearcher.getFlacText(audio, 'genre')
        meta['date'] = MetaSearcher.getFlacText(audio, 'date')
        if audio:
            meta['length'] = audio.info.length
            meta['lengthStr'] = MetaSearcher.formatLength(round(audio.info.length))
            meta['bitrate'] = str(round(audio.info.bitrate / 1000)) + ' kbps'
            meta['samplerate'] = str(round(audio.info.sample_rate / 1000)) + ' kHz'
            meta['bitspersample'] = audio.info.bits_per_sample
            meta['bpm'] = MetaSearcher.convertToNum(MetaSearcher.getFlacText(audio, ' bpm'))
        else:
            meta['length'] = 0
            meta['lengthStr'] = '0'
            meta['bitrate'] = '0 kbps'
            meta['samplerate'] = '0 kHz'
            meta['bitspersample'] = '0'
            meta['bpm'] = 0
        return meta

    def writeFlac(dir_path, songInfoForm, filename):
        audio = MetaSearcher._invokeFLAC(dir_path + '/' + filename)
        if audio:
            changed = MetaSearcher.setFlacText(audio, 'title', songInfoForm['title'].data)
            changed |= MetaSearcher.setFlacText(audio, 'album', songInfoForm['album'].data)
            changed |= MetaSearcher.setFlacText(audio, 'albumartist', songInfoForm['albumartist'].data)
            changed |= MetaSearcher.setFlacText(audio, 'artist', songInfoForm['artist'].data)
            num = MetaSearcher.convertToNum(songInfoForm['tracknumber'].data)
            if num > 0:
                changed |= MetaSearcher.setFlacText(audio, 'tracknumber', str(num))
            changed |= MetaSearcher.setFlacText(audio, 'genre', songInfoForm['genre'].data)
            changed |= MetaSearcher.setFlacText(audio, 'date', songInfoForm['date'].data)
            if changed:
                audio.pprint()
                audio.save()
        else:
            changed = False

        return changed


# filename can change too, save

    #   Returns:
    #     meta
    #       name
    #       title
    #       album
    #       albumartist
    #       artist
    #       tracknumber
    #       genre
    #       date
    #       length
    #       bitrate
    #       samplerate
    #       bitspersample (flac)
    #       bpm (flac)
    #       is_compilation *
    #       notes *
    def parseMp3(dir_path, filename):
        meta = {}
        meta['name'] = filename

        audio = MetaSearcher._invokeEasyID3(dir_path + '/' + filename)
        # meta['title'] = MetaSearcher.getId3Text(audio, 'TIT2')
        # meta['album'] = MetaSearcher.getId3Text(audio, 'TALB')
        # meta['albumartist'] = MetaSearcher.getId3Text(audio, 'TCOM')
        # meta['artist'] = MetaSearcher.getId3Text(audio, 'TPE1')
        # meta['tracknumber'] = MetaSearcher.convertToNum(MetaSearcher.getId3Text(audio, 'TRCK'))
        # meta['genre'] = MetaSearcher.getId3Text(audio, 'TCON')
        # meta['date'] = MetaSearcher.getId3Text(audio, 'TDRC')
        title = MetaSearcher.getEasyId3Text(audio, 'title')
        if not title:
            title = '<untitled>'
        meta['title'] = title
        meta['album'] = MetaSearcher.getEasyId3Text(audio, 'album')
        meta['albumartist'] = MetaSearcher.getEasyId3Text(audio, 'albumartist')
        meta['artist'] = MetaSearcher.getEasyId3Text(audio, 'artist')
        meta['tracknumber'] = MetaSearcher.convertToNum(MetaSearcher.getEasyId3Text(audio, 'tracknumber'))
        meta['genre'] = MetaSearcher.getEasyId3Text(audio, 'genre')
        meta['date'] = MetaSearcher.getEasyId3Text(audio, 'date')
        meta['bpm'] = MetaSearcher.convertToNum(MetaSearcher.getEasyId3Text(audio, 'bpm'))

        mp3 = MP3(dir_path + '/' + filename)
        meta['length'] = mp3.info.length
        meta['lengthStr'] = MetaSearcher.formatLength(round(mp3.info.length))
        bitrateModeStr = str(mp3.info.bitrate_mode)
        if ('VBR' in bitrateModeStr):
            meta['bitrate'] = str(round(mp3.info.bitrate / 1000)) + ' kbps (VBR)'
        elif ('ABR' in bitrateModeStr):
            meta['bitrate'] = str(round(mp3.info.bitrate / 1000)) + ' kbps (ABR)'
        else:
            meta['bitrate'] = str(round(mp3.info.bitrate / 1000)) + ' kbps'
        meta['samplerate'] = str(round(mp3.info.sample_rate / 1000)) + ' kHz'
        meta['bitspersample'] = 0

        return meta

    def writeMp3(dir_path, songInfoForm, filename):
        audio = MetaSearcher._invokeEasyID3(dir_path + '/' + songInfoForm.originalFilename.data)
        if audio:
            changed = MetaSearcher.setEasyId3Text(audio, 'title', songInfoForm['title'].data)
            changed |= MetaSearcher.setEasyId3Text(audio, 'album', songInfoForm['album'].data)
            changed |= MetaSearcher.setEasyId3Text(audio, 'albumartist', songInfoForm['albumartist'].data)
            changed |= MetaSearcher.setEasyId3Text(audio, 'artist', songInfoForm['artist'].data)
            num = MetaSearcher.convertToNum(songInfoForm['tracknumber'].data)
            if num > 0:
                changed |= MetaSearcher.setEasyId3Text(audio, 'tracknumber', str(num))
            changed |= MetaSearcher.setEasyId3Text(audio, 'genre', songInfoForm['genre'].data)
            changed |= MetaSearcher.setEasyId3Text(audio, 'date', songInfoForm['date'].data)
            if changed:
                audio.pprint()
                audio.save()
        else:
            changed = False

        # valid_keys = EasyID3.valid_keys.keys()
        return changed

    # Group same album names and album artists together
    def catagorize(filename, album_name_map, album_name, album_artist_map, album_artist):
        if (album_name in album_name_map):
            album_name_map[album_name].append(filename)
        else:
            names = []
            names.append(filename)
            album_name_map[album_name] = names
        if (album_artist in album_artist_map):
            album_artist_map[album_artist].append(filename)
        else:
            artists = []
            artists.append(filename)
            album_artist_map[album_artist] = artists

    def calculate_album_info(album_name_map, album_artist_map):
        # Spin through the list and find the key with the most filenames. That is our album name.
        highest = 0
        album_name = '<none>'
        album_artist = '<none>'
        for name, file_list in album_name_map.items():
            if (len(file_list) > highest):
                highest = len(file_list)
                album_name = name
        # Now spin through again and gather any filenames that are not in the main album
        files_in_other_album = []
        for name, file_list in album_name_map.items():
            if (name != album_name):
                files_in_other_album.extend(file_list)

        # Spin through the list and find the key with the most filenames. That is our album artist.
        highest = 0
        for artist, file_list in album_artist_map.items():
            if (len(file_list) > highest):
                highest = len(file_list)
                album_artist = artist
        # Now spin through again and gather any filenames that do not have the main artist
        files_with_other_artist = []
        for artist, file_list in album_artist_map.items():
            if (artist != album_artist):
                files_with_other_artist.extend(file_list)

        album_info = {}
        album_info['album_name'] = album_name
        album_info['album_artist'] = album_artist
        album_info['files_in_other_album'] = files_in_other_album
        album_info['files_with_other_artist'] = files_with_other_artist
        return album_info

    def mark_as_different(meta_list, filename, bucket):
        for meta in meta_list:
            if (filename == meta['name']):
                if 'different' not in meta:
                    meta['different'] = {}
                meta['different'][bucket] = True
                return

    def parseAlbum(dir_path, audio_files):
        album_name_map = {}
        album_artist_map = {}
        meta_list = []
        tracks_found = []
        count = 0
        for file_info in audio_files:
            filename = file_info['filename']
            if filename.lower().endswith('.flac'):
                fl = MetaSearcher.parseFlac(dir_path, filename)
            elif filename.lower().endswith('.mp3'):
                fl = MetaSearcher.parseMp3(dir_path, filename)
            fl['filenum'] = count
            fl['bytes'] = file_info['bytes']
            fl['byteStr'] = MetaSearcher.formatSize(file_info['bytes'])
            MetaSearcher.compileTrackList(tracks_found, fl)
            count += 1
            MetaSearcher.catagorize(filename, album_name_map, fl['album'], album_artist_map, fl['albumartist'])
            meta_list.append(fl)
        MetaSearcher.verifyTracksAreSequential(tracks_found)
        album_info = MetaSearcher.calculate_album_info(album_name_map, album_artist_map)
        for filename in album_info['files_in_other_album']:
            MetaSearcher.mark_as_different(meta_list, filename, 'album')
        for filename in album_info['files_with_other_artist']:
            MetaSearcher.mark_as_different(meta_list, filename, 'artist')

        audio_files_meta = {}
        audio_files_meta['album_artist'] = album_info['album_artist']
        audio_files_meta['album_name'] = album_info['album_name']
        audio_files_meta['meta_list'] = meta_list
        return audio_files_meta

    def writeSongDetails(dir_path, songInfoForm):
        filename = songInfoForm.originalFilename.data
        message = ''
        if filename.lower().endswith('.flac'):
            changed = MetaSearcher.writeFlac(dir_path, songInfoForm, filename)
        elif filename.lower().endswith('.mp3'):
            changed = MetaSearcher.writeMp3(dir_path, songInfoForm, filename)
        if changed:
            message = 'Your changes have been saved.'
        else:
            message = 'No changes made.'

        if (filename != songInfoForm['filename'].data):
            fileIo = FileIo
            target = songInfoForm['filename'].data
            rename_message = fileIo.renameFile(dir_path, filename, target)
            if rename_message != '':
                if message.endswith('saved.'):
                    message = message.replace('.', ', but the file was not renamed because: '+rename_message)
                else:
                    message = rename_message
        return message

    # Update the album information common to all files in the folder
    def changeAlbumInfo(dir_path, album_name, album_artist, normalize_file_names, strip_file_prefix):
        fileIo = FileIo
        dir = fileIo.readDir(dir_path)
        change_count = 0
        for file_info in dir['audio_files']:
            filename = file_info['filename']
            changed = False
            if filename.lower().endswith('.flac'):
                audio = MetaSearcher._invokeFLAC(dir_path + '/' + filename)
                if audio:
                    changed |= MetaSearcher.setFlacText(audio, 'album', album_name)
                    changed |= MetaSearcher.setFlacText(audio, 'albumartist', album_artist)
            else:
                audio = MetaSearcher._invokeEasyID3(dir_path + '/' + filename)
                if audio:
                    changed |= MetaSearcher.setEasyId3Text(audio, 'album', album_name)
                    changed |= MetaSearcher.setEasyId3Text(audio, 'albumartist', album_artist)
            if changed:
                audio.pprint()
                audio.save()
            if strip_file_prefix and not 'prefix to strip' in strip_file_prefix:
                if filename.startswith(strip_file_prefix):
                    new_filename = filename[len(strip_file_prefix):]
                    fileIo.renameFile(dir_path, filename, new_filename)
                    filename = new_filename
                    changed = True
            if normalize_file_names:
                start = len("")
                firstLetter = start
                for ndx in range(start, len(filename)):
                    if filename[ndx:ndx+1].isalpha():
                        break
                    firstLetter += 1
                if firstLetter > start:
                    new_filename = filename[firstLetter:]
                    fileIo.renameFile(dir_path, filename, new_filename)
                    filename = new_filename
                    changed = True
            if changed:
                change_count += 1

        change_count_str = str(change_count)
        if change_count == 1:
            return 'Added the album information changes to '+change_count_str+' file.'
        elif change_count > 0:
            return 'Added the album information changes to '+change_count_str+' files.'

        return ''

    # Invoked after a tracknumber has been incremented or decremented, this function looks for any songs
    # with a number that already occupies the new track number, and if one is found, its track
    # number will be swapped for the one the other file occupied. So, if the user moved a track from
    # 4 to 5, this method looks for another song with a 5 and if found, moves it to 4.
    def swapTracknumbers(dir_path, changed_filename, to_tracknum, current_tracknum):
        fileIo = FileIo
        dir = fileIo.readDir(dir_path)
        for file_info in dir['audio_files']:
            filename = file_info['filename']
            if filename != changed_filename:
                changed = False
                if filename.lower().endswith('.flac'):
                    audio = MetaSearcher._invokeFLAC(dir_path + '/' + filename)
                    if audio:
                        tracknum = MetaSearcher.convertToNum(MetaSearcher.getFlacText(audio, 'tracknumber'))
                        if tracknum == current_tracknum:
                            MetaSearcher.setFlacText(audio, 'tracknumber', str(to_tracknum))
                            changed = True
                else:
                    audio = MetaSearcher._invokeEasyID3(dir_path + '/' + filename)
                    if audio:
                        tracknum = MetaSearcher.convertToNum(MetaSearcher.getEasyId3Text(audio, 'tracknumber'))
                        if tracknum == current_tracknum:
                            MetaSearcher.setEasyId3Text(audio, 'tracknumber', str(to_tracknum))
                            changed = True
                if changed:
                    audio.pprint()
                    audio.save()
                    return True

        return False

    # Increment or decrement the track number of a song.
    def changeTrackNumber(dir_path, filename, direction):
        changed = False
        if filename.lower().endswith('.flac'):
            audio = MetaSearcher._invokeFLAC(dir_path + '/' + filename)
            if audio:
                tracknum = MetaSearcher.convertToNum(MetaSearcher.getFlacText(audio, 'tracknumber'))
                from_tracknum = tracknum
                if direction == 'higher':
                    tracknum += 1
                    changed = True
                elif tracknum > 1:
                    tracknum -= 1
                    changed = True
            if changed:
                MetaSearcher.setFlacText(audio, 'tracknumber', str(tracknum))
                audio.pprint()
                audio.save()
        else:
            audio = MetaSearcher._invokeEasyID3(dir_path + '/' + filename)
            if audio:
                tracknum = MetaSearcher.convertToNum(MetaSearcher.getEasyId3Text(audio, 'tracknumber'))
                from_tracknum = tracknum
                if direction == 'higher':
                    tracknum += 1
                    changed = True
                elif tracknum > 1:
                    tracknum -= 1
                    changed = True
            if changed:
                MetaSearcher.setEasyId3Text(audio, 'tracknumber', str(tracknum))
                audio.pprint()
                audio.save()

        if changed:
            MetaSearcher.swapTracknumbers(dir_path, filename, from_tracknum, tracknum)

    # Searches for song titles or album names that contain the search text
    def search(search_path, current_dir_path, search_text_list, mixOnly, artists):
        search_results = {}
        search_results['albums'] = {}
        search_results['songs'] = []
        search_results['errors'] = {}

        if len(search_text_list) > 1:
            # Exclude the current directory if this is a duplicates search
            exclude_dir = MetaSearcher.extractDirName(current_dir_path)
        else:
            exclude_dir = ''

        compressed_search_list = []
        for search_text in search_text_list:
            compressed_search_list.append(MetaSearcher.prepareTextForCompare(search_text))


        MetaSearcher.searchMeta(search_path, exclude_dir, search_results, compressed_search_list, mixOnly, artists)
        return search_results

    # Search the audio files in a directory for a match, then recursively check subdirs.
    def searchMeta(dir_path, exclude_dir, search_results, compressed_search_list, mixOnly, artists):
        fileIo = FileIo

        if exclude_dir:
            is_duplicate_search = True
        else:
            is_duplicate_search = False
        dir = fileIo.readDir(dir_path)
        current_dir = MetaSearcher.extractDirName(dir_path)
        if current_dir != exclude_dir and ((not mixOnly) or current_dir.startswith('aa')):
            # Gather meta information for the audio files in the directory
            for file_info in dir['audio_files']:
                filename = file_info['filename']
                if filename.lower().endswith('.flac'):
                    try:
                        audio = MetaSearcher._invokeFLAC(dir_path + '/' + filename)
                        for search_text in compressed_search_list:
                            MetaSearcher.searchFlac(dir_path, search_results, search_text, audio, artists, is_duplicate_search)
                    except Exception as ex:
                        if hasattr(ex, 'message'):
                            message = ex.message
                        else:
                            message = str(ex)
                        error = {}
                        error['message'] = message
                        error['filename'] = filename
                        if dir_path in search_results['errors']:
                            errors = search_results['errors'][dir_path]
                        else:
                            errors = []
                            search_results['errors'][dir_path] = errors
                        errors.append(error)
                else:
                    audio = MetaSearcher._invokeEasyID3(dir_path + '/' + filename)
                    for search_text in compressed_search_list:
                        MetaSearcher.searchEasyId3(dir_path, search_results, search_text, audio, artists,is_duplicate_search)

        # Now recursively search subdirectories
        for filename in dir['subdirs']:
            if (not mixOnly) or filename.startswith('aa'):
                MetaSearcher.searchMeta(dir_path+'/'+filename, exclude_dir, search_results,
                                        compressed_search_list, mixOnly, artists)