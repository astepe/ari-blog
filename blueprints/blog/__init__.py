from flask import Blueprint

blog = Blueprint('blog', __name__)

from blueprints.blog import views
