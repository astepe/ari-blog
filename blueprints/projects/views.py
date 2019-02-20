from flask import render_template, jsonify, abort, request
from blueprints.models import Project
from blueprints.projects import projects
from blueprints.projects.parser import SDSParser
from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField
from flask_wtf.file import FileField, FileRequired
import os
from blueprints import celery
from celery.result import AsyncResult


class SDSForm(FlaskForm):

    sds_file = FileField(validators=[FileRequired()])
    product_name = BooleanField('Product Name')
    flash_point = BooleanField('Flash Point (°F)')
    specific_gravity = BooleanField('Specific Gravity')
    cas_number = BooleanField('CAS #')
    nfpa_fire = BooleanField('NFPA Fire')
    nfpa_health = BooleanField('NFPA Health')
    nfpa_reactivity = BooleanField('NFPA Reactivity')
    sara_311 = BooleanField('SARA 311/312')
    revision_date = BooleanField('Revision Date')
    physical_state = BooleanField('Physical State')
    submit = SubmitField('Submit')


@projects.route('/celery_result', methods=['GET'])
def celery_result():

    worker_id = request.args.get('worker_id')

    result = AsyncResult(worker_id)

    if result.state == 'SUCCESS':
        return jsonify({'data': result.get()})
    else:
        return "not ready", 204


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

        worker = get_sds_data.delay(temp_file, request_keys)

        return jsonify({'worker_id': worker.id})

    return render_template("sds_parser_form.html", form=form, chemical_data={})


# currently not functioning
@celery.task()
def get_sds_data(temp_file, request_keys):
    sds_parser = SDSParser(request_keys=request_keys)
    return sds_parser.get_sds_data(temp_file, request_keys)
