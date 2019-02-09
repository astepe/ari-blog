from blueprints import create_app, make_celery
from config import Config
from celery import Celery

celery = Celery()

app = create_app(config_class=Config)
celery = make_celery(app)
app.app_context().push()
