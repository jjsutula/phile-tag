class FileIo:
    def readDir(path):

        files = []
        fl = {}
        fl['name'] = 'something.flac'
        fl['title'] = 'Some Title'
        fl['album'] = 'Some Album'
        fl['artist'] = 'Some Artist'
        fl['album_artist'] = 'Some Album Artist'
        files.append(fl)
        fl = {}
        fl['name'] = 'other.flac'
        fl['title'] = 'Other Title'
        fl['album'] = 'Other Album'
        fl['artist'] = 'Other Artist'
        fl['album_artist'] = 'Other Album Artist'
        files.append(fl)

        return files
