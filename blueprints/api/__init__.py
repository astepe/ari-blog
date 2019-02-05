from flask import Blueprint

api = Blueprint('api', __name__)

from blueprints.api import blogposts, tokens
