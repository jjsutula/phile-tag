import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template
from flask_bootstrap import Bootstrap

from .config import Config

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    cwd = os.getcwd()
    app.instance_path  = cwd + "/instance"
    app.config.from_object(Config)
    # print('key='+app.config['SECRET_KEY'])
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import album
    app.register_blueprint(album.bp)

    # app.register_error_handler(404, page_not_found)
    # app.register_error_handler(500, broblem)
    from phileTag.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')

        log_max_size = 1048576  # 1 Mb
        if ('LOG_MAX_SIZE' in app.config):
            log_max_size = app.config['LOG_MAX_SIZE']
        file_handler = RotatingFileHandler('logs/phile-tag.log', maxBytes=log_max_size,
                                        backupCount=10)
        log_format = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        if ('LOG_FORMAT' in app.config):
            log_format = app.config['LOG_FORMAT']
        file_handler.setFormatter(logging.Formatter(log_format))

        log_level = logging.WARN
        if ('LOG_LEVEL' in app.config):
            log_level = app.config['LOG_LEVEL']
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('PhileTag startup')

    bootstrap = Bootstrap(app)

    return app


def page_not_found(e):
  return render_template('404.html'), 404


def broblem(e):
  return render_template('500.html'), 500
