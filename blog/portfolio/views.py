from flask import render_template, request, url_for, Blueprint, redirect, abort
from blog.models import Project
from blog.portfolio import portfolio
from blog import db

# view list of all projects in portfolio
@portfolio.route('/portfolio', methods=['GET'])
def view_portfolio():
    return render_template("portfolio.html")

# view specific project
@portfolio.route('/portfolio/<int:id>', methods=['GET'])
def view_project(id):

    project = Project.query.get(id)
    if project != None:
        return render_template("project.html", project=project)
    abort(404)
