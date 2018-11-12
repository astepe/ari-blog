from flask import render_template, abort
from blog.models import BlogPost
from blog.blog import blog


@blog.route('/blog')
def view_blog():
    posts = BlogPost.query.all()
    return render_template('blog.html', posts=posts)


@blog.route('/blog/<int:id>', methods=['GET'])
def view_blog_post(id):

    blog_post = BlogPost.query.get(id)
    if blog_post is not None:
        return render_template('blog_post.html', blog_post=blog_post)
    abort(404)
