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
            # it's not json serializable, which prevent's it from being put
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

    # Pops the previous dir_path from the top of the stack
    def getPreviousDirHistory():
        dir_hist = RouteHelper.getDirHistory()
        if dir_hist:
            dir_path = dir_hist.pop()
            # Need to do it twice. First pop the current, then the previous.
            if dir_hist:
                dir_path = dir_hist.pop()
            session['dirhist'] = dir_hist
        else:
            dir_path = None
        return dir_path

    # Retrieve the parent of the given directory
    def getParentDir(dir_path):
        if dir_path:
            ndx = dir_path.rfind('/')
            if ndx == -1:
                ndx = dir_path.rfind('\\')
            if ndx >= -1:
                return dir_path[0:ndx]
            
        return dir_path
