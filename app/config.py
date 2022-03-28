import logging
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    LOG_MAX_SIZE = 1048576 # 1Mb
    LOG_LEVEL = logging.WARN
    LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'some-really-secret-phrasel'
    SEARCH_BASE_DIRS_STR = os.environ.get('SEARCH_BASE_DIRS') or ('~/Music')
    # Make it a list of strings
    SEARCH_BASE_DIRS = [x.strip() for x in SEARCH_BASE_DIRS_STR.split(',')]
    
    BASE_DIRS_STR = os.environ.get('BASE_DIRS') or ('~/Music')
   # Make it a list of strings
    BASE_DIRS = [x.strip() for x in BASE_DIRS_STR.split(',')]

