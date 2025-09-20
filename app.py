from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize database
with app.app_context():
    db.create_all()

# Home page
@app.route('/')
def home():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)

# Add announcement
@app.route('/add', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        author = request.form['author']
        content = request.form['content']
        new_post = Post(author=author, content=content)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('index.html', posts=Post.query.all())

# Admin page
@app.route('/admin')
def admin():
    token = request.cookies.get('admin_token')
    flag_path = os.path.join('flags', 'admin_flag.txt')
    if token == 'SECRET_ADMIN_TOKEN':
        try:
            with open(flag_path, 'r', encoding='utf-8') as f:
                flag = f.read()
            return render_template('admin.html', flag=flag)
        except FileNotFoundError:
            return "Flag file not found!", 500
    return "Unauthorized", 401

# Delete post
@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
