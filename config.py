import os

class Config(object):
    # value sourced from environment variable is preferred,
    # but if not defined by environment, hardcoded key is used
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
        '-av\x89\xe2\xf8\xab\xc3\xec\x0f\x81>B\xcf\x91\x0c<{\x16\xd2\xbe\x16%N'
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS') or False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or '/static/pictures/'