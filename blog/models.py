from blog import db
from datetime import datetime, timedelta
import base64
import os


class BlogPost(db.Model):

    __tablename__ = 'blogposts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    body = db.Column(db.Text, nullable=False)
    picture = db.Column(db.String(50), nullable=False, default='/static/pictures/python.png')

    def __repr__(self):
        return f'Title: {self.title}'

class Project(db.Model):

    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    body = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'Title : {self.title}'

class Token(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def make_token(self, expires_in=900):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        token = Token.query.filter_by(token=token).first()
        if token is None or token.token_expiration < datetime.utcnow():
            return None
        return token
