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
        meta['bitrate'] = str(round(audio.info.bitrate / 1000)) + 'kbps'
        meta['samplerate'] = str(round(audio.info.sample_rate / 1000)) + 'kHz'
        meta['bitspersample'] = audio.info.bits_per_sample
        meta['bpm'] = MetaSearcher.convertToNum(MetaSearcher.getFlacText(audio, 'bpm'))
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
            meta['bitrate'] = str(round(mp3.info.bitrate / 1000)) + 'kbps (VBR)'
        elif ('ABR' in bitrateModeStr):
            meta['bitrate'] = str(round(mp3.info.bitrate / 1000)) + 'kbps (ABR)'
        else:
            meta['bitrate'] = str(round(mp3.info.bitrate / 1000)) + 'kbps'
        meta['samplerate'] = str(round(mp3.info.sample_rate / 1000)) + 'kHz'

        return meta

