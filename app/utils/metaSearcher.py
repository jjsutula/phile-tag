from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3


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

    def getId3Text(audio, key):
        if (key in audio):
            return audio[key].text[0]
        return ''

    def getFlacText(audio, key):
        if (key in audio):
            return audio[key][0]
        return ''

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

        audio = ID3(dir_path + '/' + filename)
        meta['title'] = MetaSearcher.getId3Text(audio, 'TIT2')
        meta['album'] = MetaSearcher.getId3Text(audio, 'TALB')
        meta['albumartist'] = MetaSearcher.getId3Text(audio, 'TCOM')
        meta['artist'] = MetaSearcher.getId3Text(audio, 'TPE1')
        meta['tracknumber'] = MetaSearcher.convertToNum(MetaSearcher.getId3Text(audio, 'TRCK'))
        meta['genre'] = MetaSearcher.getId3Text(audio, 'TCON')
        meta['date'] = MetaSearcher.getId3Text(audio, 'TDRC')

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
        meta['bpm'] = 0

        return meta

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
            if (filename.endswith('.flac')):
                fl = MetaSearcher.parseFlac(dir_path, filename)
            elif (filename.endswith('.mp3')):
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
