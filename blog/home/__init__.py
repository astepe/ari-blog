from flask import Blueprint

home = Blueprint('home', __name__)

from blog.home import views
