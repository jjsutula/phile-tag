import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'some-really-secret-phrasel'
    # DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
