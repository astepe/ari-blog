from flask import Blueprint

projects = Blueprint('projects', __name__)

from blueprints.projects import views
