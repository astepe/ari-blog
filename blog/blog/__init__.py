from flask import Blueprint

blog = Blueprint('blog', __name__)

from blog.blog import views
