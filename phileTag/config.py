import logging
import os

class Config(object):
    LOG_MAX_SIZE = 1048576 # 1Mb
    LOG_LEVEL = logging.WARN
    LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'some-really-secret-phrasel'
    # DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
