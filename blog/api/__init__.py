from flask import Blueprint

api = Blueprint('api', __name__)

from blog.api import blogposts, tokens
