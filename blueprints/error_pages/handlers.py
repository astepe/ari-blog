from flask import Blueprint, render_template
from blueprints.error_pages import error_pages


@error_pages.app_errorhandler(404)
def error_404(error):
    return render_template('error_pages/error_404.html'), 404


@error_pages.app_errorhandler(500)
def error_500(error):
    return render_template('error_pages/error_500.html'), 500
