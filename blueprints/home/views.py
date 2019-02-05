from flask import render_template
from blueprints.home import home


@home.route('/')
def index():
    return render_template('index.html')
