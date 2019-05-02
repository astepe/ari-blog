from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField
from flask_wtf.file import FileField, FileRequired


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
