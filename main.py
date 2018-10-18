from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:MyNewPass@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        username_error = ''
        password_error= ''
        user = User.query.filter_by(username=username).first()
        if not username:
            username_error = 'Invalid Username'
        if not password:
            password_error = 'Invalid Password'

        if not username_error and not password_error:
            session['username'] = username
            flash('Logged in')
            return redirect('/newpost')
        
        return render_template('login.html', username_error=username_error, password_error=password_error)
    else:
        return render_template('login.html')


@app.route("/", methods=['POST', 'GET']) 
def index():
    users= User.query.all()
    return render_template('index.html', users=users)






@app.route('/blog', methods=['GET'])
def blog():
    if request.args:
        id = request.args.get('id')
        query = Blog.query.get(id)
        return render_template('singlepost.html', post=query)
    else:
        query = Blog.query.all()    
        return render_template('blog.html', blog=query)


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        title_error=''
        body_error=''
        if not title:
            title_error = "You Must Enter a Title For Your Post!"
        if not body:
            body_error = "You Must Enter A Body For Your Entry!"
        if not title_error and not body_error:
            new = Blog(title,body,owner)
            db.session.add(new)
            db.session.commit()
            return redirect('./blog?id='+ str(new.id))
    
        return render_template('newpost.html',title_error=title_error, body_error=body_error, title=title, body=body)
    else:
        return render_template('newpost.html')


if __name__ == '__main__':
    app.run()