from flask import render_template
from blog.home import home


@home.route('/')
def index():
    return render_template('index.html')
