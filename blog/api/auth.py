from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from blog.api.errors import error_response
from blog.models import Token
from flask_bcrypt import Bcrypt

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

bcrypt = Bcrypt(app=None)
PW_HASH = '$2b$12$7qyxc6GwEX8.1dt9zCtcAegSwdSkGTv.NseBRlTPUR9G9xJlZBJty'

@token_auth.verify_token
def verify_token(token):
    _token = Token.check_token(token) if token else None
    return _token is not None

@token_auth.error_handler
def token_auth_error():
    return error_response(401)

@basic_auth.verify_password
def verify_password(username, password):
    return username == 'ari' and bcrypt.check_password_hash(PW_HASH, password)

@basic_auth.error_handler
def basic_auth_error():
    return error_response(401)
