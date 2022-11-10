from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, UserMixin, login_required, logout_user
from datetime import datetime

import os

base_dir = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(base_dir, 'my_login.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = '5e0b18fd5de07e49f80cb4f8'


db = SQLAlchemy(app)
login_manager = LoginManager(app)


 
class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.Text(), nullable=False)
    def __repr__(self):
        return f"<User {self.username}>"






class Post(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    author = db.Column(db.String(255), nullable=False, unique=True)
    title = db.Column(db.String(255), nullable=False, unique=True)
    content = db.Column(db.Text(), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.author}>"


@login_manager.user_loader
def user_loader(id):
    return User.query.get(int(id))



@app.route('/')
def index():
    posts = Post.query.order_by(Post.date_created.desc()).all()
    return render_template('index.html', posts=posts)






@app.route('/post/<int:id>', methods=['POST', 'GET'])
def update(id):
    post_to_update = Post.query.get_or_404(id)

    if request.method == 'POST':
        post_to_update.author =request.form.get('author')
        post_to_update.title =request.form.get('title')
        post_to_update.content =request.form.get('content')

        db.session.commit

        return redirect(url_for('index'))

    context = {

        'post' : post_to_update
    }
    return render_template('update.html', **context)

@app.route('/addpost', methods=['POST', 'GET'])
def addpost():
   if  request.method == 'POST':
    title = request.form['title']
    author = request.form['author']
    content = request.form['content']

    post = Post(title=title, author=author, content=content, date_created=datetime.now())

    db.session.add(post)
    db.session.commit()

    return redirect(url_for('index'))

   return render_template('post.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))








@app.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        user = User.query.filter_by(username=username).first()
        if user:
            return redirect(url_for('register'))

        email_exists = User.query.filter_by(email=email).first()
        if email_exists:
            return redirect(url_for('register'))

        password_hash = generate_password_hash(password)

        new_user = User(username=username, email=email, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')




with app.app_context():
    db.create_all()





if __name__=="__main__":
    app.run(debug=True)