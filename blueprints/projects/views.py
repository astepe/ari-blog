from flask import render_template, jsonify, abort
from blueprints.models import Project
from blueprints.projects import projects
from sdsparser import SDSParser
from .forms import SDSForm
import os


# view list of all projects
@projects.route('/projects', methods=['GET'])
def view_projects():
    return render_template("projects.html")


# view specific project
@projects.route('/projects/<int:id>', methods=['GET'])
def view_project(id):

    project = Project.query.get(id)
    if project is not None:
        return render_template("project.html", project=project)
    abort(404)


@projects.route('/projects/submit_sds', methods=['GET', 'POST'])
def submit_sds():

    form = SDSForm()

    if form.validate_on_submit():

        request_keys = []
        for field in form:
            if field.data:
                request_keys.append(field.name)

        temp_file = os.getcwd() + '/tempsds.pdf'
        form.sds_file.data.save(temp_file)

        sds_parser = SDSParser(request_keys=request_keys)
        sds_data = sds_parser.get_sds_data(temp_file)

        return jsonify({'sds_data': sds_data})

    return render_template("sds_parser_form.html", form=form, chemical_data={})
