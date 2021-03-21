from pathlib import Path

# File I/O helper functions
class FileIo:

    # ****************
    # Public methods
    # ****************

    # Returns a dictionary containing information about files in the directory. Structure:
    # dir
    #   audio_files (string array of names of all *.flac, *.mp3)
    #   other_files (string array of names of all other files)
    #   subdirs (string array contains all subdirectory names)
    #   error - any error that occurs here
    #
    #   A later step will gather the following information about each audio_file:
    #   audio_file (map that contains information about each *.flac, *.mp3)
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
        subdirs = []
        for f in sorted(dirpath.iterdir()):
            if f.is_file():
                filename = f.name
                # Empty files are never treated as audio files regardless of their suffix
                if Path(f).stat().st_size == 0:
                    other_files.append(filename)
                elif (filename.lower().endswith('.flac')):
                    # meta = get_flac_meta(f)
                    audio_files.append(filename)
                elif (filename.lower().endswith('.mp3')):
                    # meta = get_mp3_meta(f)
                    audio_files.append(filename)
                else:
                    other_files.append(filename)
            elif f.is_dir():
                subdirs.append(f.name)

        dir['audio_files'] = audio_files
        dir['other_files'] = other_files
        dir['subdirs'] = subdirs

        return dir

    # Renames the given file on the drive
    def renameFile(dir_path, original, target):
        if original.lower().endswith('.flac') and not target.lower().endswith('.flac'):
            if target.lower().endswith('.mp3'):
                return 'Cannot convert a FLAC file to an MP3 by simply renaming.'
            else:
                target += '.flac'
        if original.lower().endswith('.mp3') and not target.lower().endswith('.mp3'):
            if target.lower().endswith('.flac'):
                return 'Cannot convert an MP3 file to a FLAC by simply renaming.'
            else:
                target += '.mp3'
        if target.endswith('.FLAC'):
            target = target.replace('.FLAC', '.flac')
        if target.endswith('.MP3'):
            target = target.replace('.MP3', '.mp3')
        target_path_name = dir_path + '/' + target
        target_path = Path(target_path_name)
        if (target_path.exists()):
            return 'Cannot rename '+dir_path+'/'+original+' to '+target+'. A file by that name already exists.'

        original_path_name = dir_path + '/' + original
        original_path = Path(original_path_name)
        original_path.rename(target_path)
        return ''
