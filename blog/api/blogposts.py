from flask import jsonify, request, current_app
from blog.api import api
from blog import db
from blog.models import BlogPost
from blog.api.errors import bad_request, not_found
from blog.api.auth import token_auth
import os
from blog.api.s3 import make_s3_signature

from PIL import Image

DEFAULT_PIC = '/static/pictures/python.png'
basedir = ''

@api.route('/blogposts/<int:id>', methods=['GET'])
@token_auth.login_required
def get_blogpost(id):

    post = BlogPost.query.get(id)
    if post == None:
        return not_found('the post could not be found')
    return jsonify({'id': post.id, 'title': post.title, 'body': post.body, 'date': post.date, 'picture': post.picture})


@api.route('/blogposts', methods=['GET'])
@token_auth.login_required
def get_blogposts():

    posts = BlogPost.query.all()

    list = []
    for post in posts:
        list.append({'id': post.id, 'title': post.title, 'body': post.body, 'date': post.date, 'picture': post.picture})
    return jsonify(list)


@api.route('/blogposts/create', methods=['POST'])
@token_auth.login_required
def create_blog_post():

    data = request.get_json() or {}

    if 'title' not in data or 'body' not in data:
        return bad_request('must include title and body')

    blogpost = BlogPost(title=data['title'], body=data['body'])

    db.session.add(blogpost)
    db.session.commit()

    data['id'] = BlogPost.query.filter_by(title=data['title']).first().id

    signature = {}

    if 'image' in data:
        signature = make_s3_signature(data['image'])
        data.update(signature)

    return jsonify(data)


@api.route('/blogposts/<int:id>/update', methods=['PUT'])
@token_auth.login_required
def update_blog_post(id):

    data = request.get_json() or {}
    blogpost = BlogPost.query.get_or_404(id)

    if 'title' in data and blogpost.title != data['title']:
        blogpost.title = data['title']

    if 'body' in data:
        blogpost.body = data['body']

    db.session.commit()

    if 'image' in data:
        signature = make_s3_signature(data['image'])
        print('image:', data['image'], 'signature:', signature)
        data.update(signature)

    return jsonify(data)


@api.route('/blogposts/<int:id>/delete', methods=['DELETE'])
@token_auth.login_required
def delete_blog_post(id):

    blogpost = BlogPost.query.filter_by(id=id).first()
    if blogpost == 0:
        return not_found('the post could not be found')
    if blogpost.picture != DEFAULT_PIC and \
                            os.path.exists(basedir + blogpost.picture):
        os.remove(basedir + blogpost.picture)

    db.session.delete(blogpost)
    db.session.commit()

    return jsonify({'message': f'post_id {id} has been deleted'})
