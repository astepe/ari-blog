from flask import jsonify
from blog.api import api
from blog import db
from datetime import datetime
from blog.api.auth import basic_auth
from blog.models import Token

@api.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = Token().make_token()
    now = datetime.utcnow()
    db.session.commit()
    return jsonify({'token': token})

# g.current_user implementation not fully understood yet
# will need to go through tutorial to understand
#@api.route('/tokens', methods=['DELETE'])
#@basic_auth.login_required
#def revoke_token():
#    g.current_user.evoke_token()
#    db.session.commit()
#    return '', 204
