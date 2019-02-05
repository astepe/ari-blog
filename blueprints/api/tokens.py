from flask import jsonify
from blueprints.api import api
from blog import db
from datetime import datetime
from blueprints.api.auth import basic_auth
from blueprints.models import Token


@api.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = Token().make_token()
    now = datetime.utcnow()
    db.session.commit()
    return jsonify({'token': token})
