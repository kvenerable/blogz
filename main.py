from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    
    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog', methods=['GET'])
def blog():
    blogs = Blog.query.all()

    if request.args:
        blog_id = request.args.get('id')
        blog_post = Blog.query.get(blog_id)

        return render_template('blog_entry.html', blog_post=blog_post)

    return render_template('blog.html', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    title_error = ""
    body_error = ""

    if request.method == 'POST' :
        title = request.form['title']
        body = request.form['body']

        if len(title) == 0:
            title_error = "Invalid title"
            
        if len(body) == 0:
            body_error = "Invalid body"

        if not len(title) == 0 and not len(body) == 0:
            blog_post = Blog(title, body)
            db.session.add(blog_post)
            db.session.commit()
            id = blog_post.id
            return redirect('/blog?id={0}'.format(id))
            
        else:
            return render_template("newpost.html",
            title=title,
            body=body,
            title_error=title_error,
            body_error=body_error )

    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()