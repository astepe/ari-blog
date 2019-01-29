from flask import render_template, jsonify, abort
from blog.models import Project
from blog.projects import projects
from blog.projects.parser import SDSParser
from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField
from flask_wtf.file import FileField, FileRequired
import os


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
        sds_data = sds_parser.get_sds_data(temp_file, request_keys)

        return jsonify({'data': sds_data})

    return render_template("sds_parser_form.html", form=form, chemical_data={})
