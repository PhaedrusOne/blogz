from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:MyNewPass@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


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

@app.before_request
def require_login():
    allowed_routes = ['login','index','singleUser','signup','list_blogs']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


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
        if user and user.password == password:
            session['username'] = username
            return redirect('/list_blogs')
        else:
            password_error = 'Invalid Password'
        return render_template('login.html', username_error=username_error, password_error=password_error)
    
    return render_template('login.html')

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        username_val = ""  
        password_val = ""  
        verify_val = ""
        user_exist = ""
        duplicate_user = User.query.filter_by(username=username).first()

        if duplicate_user:
            username_val = "Duplicate User"
            
        if username == "":
            username_val = "Empty field"
            
        elif len(username) < 3 or len(username) > 20:
            username_val = "Username has to contain no less than 3 and not more than 20 characters"    
                
        elif " " in username:
            username_error = "Your username cannot contain any spaces."
        
        if password == "":
            password_val = "Empty field"
            
        elif len(password) < 3 or len(password) > 20:
            password_val = "Password cannot contain no less than 3 and no more than 20 characters"
            
        elif " " in password:
            password_val = "Your password cannot contain any spaces."
            
        if verify == "":
            verify_val = "Empty field"
            
        elif verify != password:
            verify_val = "Issue with verification. Try again" 
        
        if not duplicate_user and not username_val and not password_val and not verify_val:
            user = User(username, password)
            db.session.add(user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            return render_template('signup.html',
            username_val=username_val, password_val=password_val, verify_val=verify_val, username=username)
    return render_template('signup.html')
      

@app.route('/', methods=['POST', 'GET']) 
def index():
        users= User.query.all()
        return render_template('index.html', users=users)


@app.route('/singleUser', methods=['POST','GET'])
def singleUser():
    user = request.args.get('user')
    blogs = Blog.query.filter_by(owner_id=user).all()
    return render_template('singleUser.html', blogs=blogs)


@app.route('/list_blogs', methods=['GET'])
def list_blogs():
    if request.args:
        id = request.args.get('id')
        query = Blog.query.get(id)
        return render_template('entry.html', post=query)
    else:
        query = Blog.query.all()    
        return render_template('list_blogs.html', blog=query)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
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
            return redirect('/list_blogs?id='+ str(new.id))
    
        return render_template('newpost.html',title_error=title_error, body_error=body_error, title=title, body=body, owner=owner)
    else:
        return render_template('newpost.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')


if __name__ == '__main__':
    app.run()