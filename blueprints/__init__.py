from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from celery import Celery

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from blueprints import models

    from blueprints.home import home
    from blueprints.projects import projects
    from blueprints.blog import blog
    from blueprints.error_pages import error_pages
    from blueprints.api import api

    app.register_blueprint(home)
    app.register_blueprint(blog)
    app.register_blueprint(projects)
    app.register_blueprint(error_pages)
    app.register_blueprint(api, url_prefix='/api')

    from blueprints.blog.blog_filter import blog_filter

    app.jinja_env.filters['blog_filter'] = blog_filter

    if not app.testing:
        pass

    return app


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
