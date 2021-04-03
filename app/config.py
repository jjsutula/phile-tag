import logging
import os

class Config(object):
    LOG_MAX_SIZE = 1048576 # 1Mb
    LOG_LEVEL = logging.WARN
    LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'some-really-secret-phrasel'
    SEARCH_BASE_DIRS = ('/media/jon/Dell USB Portable HDD/laphroig/mirror/music','/media/jon/Dell USB Portable HDD/kts-hirez')

    BASE_DIRS = ('/media/jon/Dell USB Portable HDD/laphroig/mirror/music','/media/jon/Dell USB Portable HDD/kts-hirez','/run/user/1000/gvfs/smb-share:server=nononas.local,share=multimedia/jon')

