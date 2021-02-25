from pathlib import Path
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
# from app.utils.meta import Meta


# Returns a dictionary containing information about files in the directory. Structure:
# dir
#   audio_files (string array of names of all *.flac, *.mp3)
#   other_files (string array of names of all other files)
#   subdirs (string array contains all subdirectory names)
#   error - any error that occurs here
#
#   A later step will gather the following information about each audio_file:
#   audio_file (map that contains information about each *.flac, *.mp3)
#     file_name
#     file_size
#     duration
#     meta
#       title
#       album_name
#       artist
#       album_artist
#       genre
#       year
#       is_compilation
#       notes
class FileIo:

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
    def readDir(dir_path):
        dir = {}
        # path = Path(dir_path).glob('**/*')
        # files = [f for f in path if f.is_file() and f.i]
        dirpath = Path(dir_path)
        if not (dirpath.exists()):
            dir['error'] = "Directory '" + dir_path + "' does not exist"
            return dir
        elif not (dirpath.is_dir()):
            dir['error'] = "Path '" + dir_path + "' is not a valid directory"
            return dir

        audio_files = []
        other_files = []
        for f in sorted(dirpath.iterdir()):
            if f.is_file():
                filename = f.name
                if (filename.endswith('.flac')):
                    # meta = get_flac_meta(f)
                    audio_files.append(filename)
                elif (filename.endswith('.mp3')):
                    # meta = get_mp3_meta(f)
                    audio_files.append(filename)
                else:
                    other_files.append(filename)
            elif f.is_dir():
                other_files.append('*'+f.name)

        dir['audio_files'] = audio_files
        dir['other_files'] = other_files
        return dir


#   Returns:
#     meta
#       title
#       tracknumber
#       album
#       artist
#       albumartist
#       genre
#       date
#       length
#       bpm
#       bitrate (mp3)
#       is_compilation *
#       notes *
    def parseFlac(dir_path, filename):
        meta = {}
        meta['name'] = filename
        audio = FLAC(dir_path + '/' + filename)
        meta['title'] = FileIo.getFlacText(audio, 'title')
        meta['artist'] = FileIo.getFlacText(audio, 'artist')
        meta['album'] = FileIo.getFlacText(audio, 'album')
        meta['date'] = FileIo.getFlacText(audio, 'date')
        meta['tracknumber'] = FileIo.convertToNum(FileIo.getFlacText(audio, 'tracknumber'))
        meta['genre'] = FileIo.getFlacText(audio, 'genre')
        meta['albumartist'] = FileIo.getFlacText(audio, 'albumartist')
        meta['bpm'] = FileIo.convertToNum(FileIo.getFlacText(audio, 'bpm'))
        meta['length'] = FileIo.formatLength(round(audio.info.length))
        meta['bitrate'] = str(round(audio.info.bitrate / 1000)) + 'kbps'
        meta['sample_rate'] = str(round(audio.info.sample_rate / 1000)) + 'kHz'
        meta['bits_per_sample'] = audio.info.bits_per_sample
        return meta


    def parseMp3(dir_path, filename):
        meta = {}
        meta['name'] = filename
        mp3 = MP3(dir_path + '/' + filename)
        meta['length'] = FileIo.formatLength(round(mp3.info.length))
        bitrateModeStr = str(mp3.info.bitrate_mode)
        if ('VBR' in bitrateModeStr):
            meta['bitrate'] = str(round(mp3.info.bitrate / 1000)) + 'kbps (VBR)'
        elif ('ABR' in bitrateModeStr):
            meta['bitrate'] = str(round(mp3.info.bitrate / 1000)) + 'kbps (ABR)'
        else:
            meta['bitrate'] = str(round(mp3.info.bitrate / 1000)) + 'kbps'
        meta['sample_rate'] = str(round(mp3.info.sample_rate / 1000)) + 'kHz'

        audio = ID3(dir_path + '/' + filename)
        meta['artist'] = FileIo.getId3Text(audio, 'TPE1')
        meta['album'] = FileIo.getId3Text(audio, 'TALB')
        meta['title'] = FileIo.getId3Text(audio, 'TIT2')
        meta['date'] = FileIo.getId3Text(audio, 'TDRC')
        meta['tracknumber'] = FileIo.convertToNum(FileIo.getId3Text(audio, 'TRCK'))
        meta['genre'] = FileIo.getId3Text(audio, 'TCON')
        meta['albumartist'] = FileIo.getId3Text(audio, 'TCOM')

        return meta
