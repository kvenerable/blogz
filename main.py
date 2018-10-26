from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'



class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password
        

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')
        

@app.route('/blog', methods=['GET'])
def blog():

    
    blog_id = request.args.get('id')
    blog_user = request.args.get('user')

    if blog_id:
        blog_post = Blog.query.get(blog_id)
        return render_template('blog_entry.html', blog_post=blog_post)

    if blog_user:
        user = User.query.filter_by(username=blog_user).first()
        blog_post = Blog.query.filter_by(owner=user).all()
        return render_template('singleUser.html', blog_post=blog_post, username=blog_user)

    else:
        blog_post = Blog.query.all()
        return render_template('blog.html', title="Build a Blog", blog_post=blog_post)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    owner = User.query.filter_by(username=session['username']).first()
    

    title_error = ""
    body_error = ""

    if request.method == 'POST' :
        title = request.form['title']
        body = request.form['body']

        if len(title) == 0:
            title_error = "Invalid title"
            
        if len(body) == 0:
            body_error = "Invalid body"

        if len(title) != 0 and len(body) !=  0:
            blog_post = Blog(title, body, owner)
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

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')
            
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username_error = ''
    password_error = ''
    verify_error = ''
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        
        if len(username) == 0 or len(username) < 3 or len(username) >20 or " " in username:
        	username_error = 'Not a valid username'
		
        if len(password) == 0 or len(password) < 3 or len(password) >20 or " " in password:
            password_error= "Not a valid password"
            password = ""
		
        if len(verify) == 0 or len(verify) < 3 or len(password) > 20 or " " in password:
            verify_error = "Invalid password"

        if verify != password:
            verify_error = 'Passwords dont match'
            verify = " "
            password = " "
				
                
        if not username_error and not password_error and not verify_error:
            existing_user = User.query.filter_by(username=username).first()
            
            if not existing_user:	
			# if a user doesn't exist:
				# do the following
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')

            if existing_user:
                flash("User already exist")
                return render_template('signup.html')
			# if user exists:
				# send an error message back
				# render the signup.html template
        else:
        # else, render the template with error message(s) and preserve username
            return render_template('signup.html', 
            username_error = username_error, 
            password_error = password_error,
            verify_error = verify_error,
            username = username)

    return render_template('signup.html') 




@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all() 
    return render_template ('index.html', users=users)


if __name__ == '__main__':
    app.run()