import os

from flask import Flask, render_template
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

    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, broblem)

    return app


def page_not_found(e):
  return render_template('404.html'), 404


def broblem(e):
  return render_template('500.html'), 500
