import os


class Config(object):

    SECRET_KEY = os.environ.get('APP_SECRET_KEY')
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'default'
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS') or False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or '/static/images/'
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
    BROKER_URL = os.environ.get('REDIS_URL') or 'redis://localhost/0'
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL') or 'redis://localhost/0'
