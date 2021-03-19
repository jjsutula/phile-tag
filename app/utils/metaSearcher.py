from app.utils.fileio import FileIo
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

# NOTE: See https://code.google.com/archive/p/mutagen/wikis/Tutorial.wiki

class MetaSearcher:

    # ****************
    # Internal helper methods
    # ****************
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

    def convertToNum(value):
        if (value.isnumeric()):
            return int(value)
        return 0

    def getEasyId3Text(audio, key):
        if (key in audio):
            return audio[key][0]
        return ''

    def getId3Text(audio, key):
        if (key in audio):
            return audio[key].text[0]
        return ''

    def setEasyId3Text(audio, key, text):
        changed = False
        if text:
            if key not in audio or audio[key][0] != text:
                audio[key] = text
                changed = True
        return changed

    def getFlacText(audio, key):
        if (key in audio):
            return audio[key][0]
        return ''

    def setFlacText(audio, key, text):
        changed = False
        if text:
            if key not in audio or audio[key][0] != text:
                audio[key] = text
                changed = True
        return changed

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
        audio = FLAC(dir_path + '/' + filename)
        meta['title'] = MetaSearcher.getFlacText(audio, 'title')
        meta['album'] = MetaSearcher.getFlacText(audio, 'album')
        meta['albumartist'] = MetaSearcher.getFlacText(audio, 'albumartist')
        meta['artist'] = MetaSearcher.getFlacText(audio, 'artist')
        meta['tracknumber'] = MetaSearcher.convertToNum(MetaSearcher.getFlacText(audio, 'tracknumber'))
        meta['genre'] = MetaSearcher.getFlacText(audio, 'genre')
        meta['date'] = MetaSearcher.getFlacText(audio, 'date')
        meta['length'] = MetaSearcher.formatLength(round(audio.info.length))
        meta['bitrate'] = str(round(audio.info.bitrate / 1000)) + ' kbps'
        meta['samplerate'] = str(round(audio.info.sample_rate / 1000)) + ' kHz'
        meta['bitspersample'] = audio.info.bits_per_sample
        meta['bpm'] = MetaSearcher.convertToNum(MetaSearcher.getFlacText(audio, ' bpm'))
        return meta

    def writeFlac(dir_path, songInfoForm, filename):
        audio = FLAC(dir_path + '/' + filename)
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

        audio = EasyID3(dir_path + '/' + filename)
        # meta['title'] = MetaSearcher.getId3Text(audio, 'TIT2')
        # meta['album'] = MetaSearcher.getId3Text(audio, 'TALB')
        # meta['albumartist'] = MetaSearcher.getId3Text(audio, 'TCOM')
        # meta['artist'] = MetaSearcher.getId3Text(audio, 'TPE1')
        # meta['tracknumber'] = MetaSearcher.convertToNum(MetaSearcher.getId3Text(audio, 'TRCK'))
        # meta['genre'] = MetaSearcher.getId3Text(audio, 'TCON')
        # meta['date'] = MetaSearcher.getId3Text(audio, 'TDRC')
        meta['title'] = MetaSearcher.getEasyId3Text(audio, 'title')
        meta['album'] = MetaSearcher.getEasyId3Text(audio, 'album')
        meta['albumartist'] = MetaSearcher.getEasyId3Text(audio, 'albumartist')
        meta['artist'] = MetaSearcher.getEasyId3Text(audio, 'artist')
        meta['tracknumber'] = MetaSearcher.convertToNum(MetaSearcher.getEasyId3Text(audio, 'tracknumber'))
        meta['genre'] = MetaSearcher.getEasyId3Text(audio, 'genre')
        meta['date'] = MetaSearcher.getEasyId3Text(audio, 'date')
        meta['bpm'] = MetaSearcher.convertToNum(MetaSearcher.getEasyId3Text(audio, 'bpm'))

        mp3 = MP3(dir_path + '/' + filename)
        meta['length'] = MetaSearcher.formatLength(round(mp3.info.length))
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
        audio = EasyID3(dir_path + '/' + songInfoForm.originalFilename.data)
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

    def mark_as_different(meta_list, filename):
        for meta in meta_list:
            if (filename == meta['name']):
                meta['different'] = True
                return

    def parseAlbum(dir_path, audio_files):
        album_name_map = {}
        album_artist_map = {}
        meta_list = []
        count = 0
        for filename in audio_files:
            if filename.lower().endswith('.flac'):
                fl = MetaSearcher.parseFlac(dir_path, filename)
            elif filename.lower().endswith('.mp3'):
                fl = MetaSearcher.parseMp3(dir_path, filename)
            fl['filenum'] = count
            count += 1
            MetaSearcher.catagorize(filename, album_name_map, fl['album'], album_artist_map, fl['albumartist'])
            meta_list.append(fl)
        album_info = MetaSearcher.calculate_album_info(album_name_map, album_artist_map)
        for filename in album_info['files_in_other_album']:
            MetaSearcher.mark_as_different(meta_list, filename)
        for filename in album_info['files_with_other_artist']:
            MetaSearcher.mark_as_different(meta_list, filename)

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
    def changeAlbumInfo(dir_path, album_name, album_artist, normalize_file_names):
        fileIo = FileIo
        dir = fileIo.readDir(dir_path)
        change_count = 0
        for filename in dir['audio_files']:
            changed = False
            if filename.lower().endswith('.flac'):
                audio = FLAC(dir_path + '/' + filename)
                changed |= MetaSearcher.setFlacText(audio, 'album', album_name)
                changed |= MetaSearcher.setFlacText(audio, 'albumartist', album_artist)
            else:
                audio = EasyID3(dir_path + '/' + filename)
                changed |= MetaSearcher.setEasyId3Text(audio, 'album', album_name)
                changed |= MetaSearcher.setEasyId3Text(audio, 'albumartist', album_artist)
            firstLetter = 0
            if changed:
                audio.pprint()
                audio.save()
            if normalize_file_names:
                for ndx in range(0, len(filename)):
                    if filename[ndx:ndx+1].isalpha():
                        break
                    firstLetter += 1
                if firstLetter > 0:
                    new_filename = filename[firstLetter:]
                    fileIo.renameFile(dir_path, filename, new_filename)
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
        for filename in dir['audio_files']:
            if filename != changed_filename:
                changed = False
                if filename.lower().endswith('.flac'):
                    audio = FLAC(dir_path + '/' + filename)
                    tracknum = MetaSearcher.convertToNum(MetaSearcher.getFlacText(audio, 'tracknumber'))
                    if tracknum == current_tracknum:
                        MetaSearcher.setFlacText(audio, 'tracknumber', str(to_tracknum))
                        changed = True
                else:
                    audio = EasyID3(dir_path + '/' + filename)
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
            audio = FLAC(dir_path + '/' + filename)
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
            audio = EasyID3(dir_path + '/' + filename)
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
