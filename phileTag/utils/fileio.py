from pathlib import Path


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

        # files = []

        # fl = {}
        # fl['name'] = 'something.flac'
        # fl['title'] = 'Some Title'
        # fl['album'] = 'Some Album'
        # fl['artist'] = 'Some Artist'
        # fl['album_artist'] = 'Some Album Artist'
        # files.append(fl)
        # fl = {}
        # fl['name'] = 'other.flac'
        # fl['title'] = 'Other Title'
        # fl['album'] = 'Other Album'
        # fl['artist'] = 'Other Artist'
        # fl['album_artist'] = 'Other Album Artist'
        # files.append(fl)

        # return files
