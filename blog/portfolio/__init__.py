from flask import Blueprint

portfolio = Blueprint('portfolio', __name__)

from blog.portfolio import views
