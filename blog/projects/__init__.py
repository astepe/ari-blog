from flask import Blueprint

projects = Blueprint('projects', __name__)

from blog.projects import views
