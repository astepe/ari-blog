import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['DEBUG'] = True

    db.init_app(app)
    migrate.init_app(app, db)

    from blog import models

    from blog.portfolio import portfolio
    from blog.blog import blog
    from blog.error_pages import error_pages
    from blog.api import api

    app.register_blueprint(blog)
    app.register_blueprint(portfolio)
    app.register_blueprint(error_pages)
    app.register_blueprint(api, url_prefix='/api')

    if not app.testing:
        pass

    return app
