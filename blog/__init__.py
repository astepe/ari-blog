from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from blog import models

    from blog.home import home
    from blog.portfolio import portfolio
    from blog.blog import blog
    from blog.error_pages import error_pages
    from blog.api import api

    app.register_blueprint(home)
    app.register_blueprint(blog)
    app.register_blueprint(portfolio)
    app.register_blueprint(error_pages)
    app.register_blueprint(api, url_prefix='/api')

    from blog.blog.blog_filter import blog_filter

    app.jinja_env.filters['blog_filter'] = blog_filter

    if not app.testing:
        pass

    return app
