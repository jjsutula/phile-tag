from app.utils.fileio import FileIo
from flask import session

# Helper functions used by the route module
class RouteHelper:

    # ****************
    # Public methods
    # ****************

    # Retrieve the directory history from the session
    def getDirHistory():
        if 'dirhist' in session:
            dir_hist = session['dirhist']
        else:
            # The deque class is more efficient than a List for a stack, but
            # it's not json serializable, which prevents it from being put
            # in the session without special encoding and decoding. So use List.
            dir_hist = []
            session['dirhist'] = dir_hist
        return dir_hist

    # Appends the dir_path to the top of the stack, unless it is already there
    def putDirHistory(dir_path):
        dir_hist = RouteHelper.getDirHistory()
        if dir_hist:
            if dir_hist[-1] != dir_path:
                dir_hist.append(dir_path)
                session['dirhist'] = dir_hist
        else:
            dir_hist.append(dir_path)
            session['dirhist'] = dir_hist

    # Returns the previous sibling from the parent
    def getPreviousDir(dir_path):
        parent = RouteHelper.getParentDir(dir_path)
        if parent:
            fileIo = FileIo
            parent_dir = fileIo.readDir(parent)
            previous = None
            for dir_name in parent_dir['subdirs']:
                if dir_path.endswith('/'+dir_name) or dir_path.endswith('\\'+dir_name):
                    if previous:
                        return previous
                    return parent
                previous = parent+'/'+dir_name
        return dir_path

    # Returns the next sibling from the parent
    def getNextDir(dir_path):
        parent = RouteHelper.getParentDir(dir_path)
        if parent:
            fileIo = FileIo
            parent_dir = fileIo.readDir(parent)
            found_current = False
            for dir_name in parent_dir['subdirs']:
                if found_current:
                    # This is the directory immediately after the current dir, so it's the 'next'
                    return parent+'/'+dir_name
                elif dir_path.endswith('/'+dir_name) or dir_path.endswith('\\'+dir_name):
                    found_current = True

        return parent

    # Retrieve the parent of the given directory
    def getParentDir(dir_path):
        if dir_path:
            ndx = dir_path.rfind('/')
            if ndx == -1:
                ndx = dir_path.rfind('\\')
            if ndx >= -1:
                return dir_path[0:ndx]
            
        return dir_path
