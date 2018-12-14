from flask import render_template, abort, jsonify, request
from blog.models import Project
from blog.projects import projects
from blog.projects.parser import sds_parser
from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField
from flask_wtf.file import FileField, FileRequired
import os


class SDSForm(FlaskForm):

    sds_file = FileField(validators=[FileRequired()])
    product_name = BooleanField('Product Name', default='checked')
    flash_point = BooleanField('Flash Point', default='checked')
    specific_gravity = BooleanField('Specific Gravity', default='checked')
    cas_number = BooleanField('CAS #', default='checked')
    nfpa = BooleanField('NFPA Ratings', default='checked')
    sara_311 = BooleanField('SARA 311/312', default='checked')
    revision_date = BooleanField('Revision Date', default='checked')
    physical_state = BooleanField('Physical State', default='checked')
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

    if request.method == 'GET':

        return render_template("sds_parser_form.html", form=form, chemical_data={})

    elif form.validate_on_submit():

        temp_file = os.getcwd() + '/tempsds.pdf'
        form.sds_file.data.save(temp_file)
        chemical_data = sds_parser(temp_file)

        return render_template('sds_parser_form.html', form=form, chemical_data=chemical_data)

    else:

        return jsonify(data={'message': 'nope'})
