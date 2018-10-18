from flask import jsonify, request, current_app
from blog.api import api
from blog import db
from blog.models import BlogPost
from blog.api.errors import bad_request, not_found
from blog.api.auth import token_auth
import os, sys, boto3, mimetypes
from PIL import Image

DEFAULT_PIC = '/static/images/python.png'
basedir = ''

@api.route('/blogposts/<int:id>', methods=['GET'])
@token_auth.login_required
def get_blogpost(id):

    post = BlogPost.query.get(id)
    if post == None:
        return not_found('the post could not be found')
    return jsonify({'id': post.id, 'title': post.title, 'body': post.body, 'date': post.date, 'image': post.image})


@api.route('/blogposts', methods=['GET'])
@token_auth.login_required
def get_blogposts():

    posts = BlogPost.query.all()

    list = []
    for post in posts:
        list.append({'id': post.id, 'title': post.title, 'body': post.body, 'date': post.date, 'image': post.image})
    return jsonify(list)


@api.route('/blogposts/create', methods=['POST'])
@token_auth.login_required
def create_blog_post():

    data = request.get_json() or {}

    if 'title' not in data or 'body' not in data:
        return bad_request('must include title and body')

    blogpost = BlogPost(title=data['title'], body=data['body'])

    print(data['title'])

    if 'image' in data:
        blogpost.image = data['image']

    db.session.add(blogpost)
    db.session.commit()

    data['id'] = BlogPost.query.filter_by(title=data['title']).first().id

    return jsonify(data)


@api.route('/blogposts/<int:id>/update', methods=['PUT'])
@token_auth.login_required
def update_blog_post(id):

    data = request.get_json() or {}
    blogpost = BlogPost.query.get_or_404(id)

    if 'title' in data:
        blogpost.title = data['title']

    if 'body' in data:
        blogpost.body = data['body']

    if 'image' in data:
        blogpost.image = data['image']

    db.session.commit()

    return jsonify(data)


@api.route('/blogposts/<int:id>/delete', methods=['DELETE'])
@token_auth.login_required
def delete_blog_post(id):

    blogpost = BlogPost.query.filter_by(id=id).first()
    if blogpost == 0:
        return not_found('the post could not be found')
    if blogpost.image != DEFAULT_PIC and \
                            os.path.exists(basedir + blogpost.image):
        os.remove(basedir + blogpost.image)

    db.session.delete(blogpost)
    db.session.commit()

    return jsonify({'message': f'post_id {id} has been deleted'})


@api.route('/sign_s3/<string:file_name>', methods=['GET'])
@token_auth.login_required
def sign_s3(file_name):

        S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')

        s3 = boto3.client('s3')

        data = request.get_json()

        file_name = file_name.replace(' ', '_').lower()

        mime_type = mimetypes.guess_type(file_name)[0]

        ext_type = file_name.split('.')[-1]

        if ext_type not in set(['png', 'jpg', 'jpeg', 'gif']):

            return bad_file_type('file type unsupported')

        presigned_post = s3.generate_presigned_post(
            Bucket = S3_BUCKET_NAME,
            Key = file_name,
            Fields = {"acl": "public-read", "Content-Type": mime_type},
            Conditions = [
              {"acl": "public-read"},
              {"Content-Type": mime_type}
            ],
            ExpiresIn = 3600
        )

        return jsonify({
            'data': presigned_post,
            'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET_NAME, file_name)
          })
