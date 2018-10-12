from flask import render_template, request, url_for, redirect, abort
from blog.models import BlogPost
from blog.blog import blog
from blog import db


@blog.route('/')
@blog.route('/blog')
def view_blog():
    posts = BlogPost.query.all()
    return render_template('blog.html', posts=posts)


@blog.route('/blog/<int:id>', methods=['GET'])
def view_blog_post(id):

    blog_post = BlogPost.query.get(id)
    if blog_post != None:
        return render_template('blog_post.html', blog_post=blog_post)
    abort(404)
