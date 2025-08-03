from flask import Flask, render_template, request, redirect, url_for, session
import json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback_key")

USERS_FILE = 'users.json'

# Utilities to load/save users
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

@app.route('/')
def splash():
    return render_template('splash.html')

@app.route('/login')
def login():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/register', methods=['POST'])
def register():
    users = load_users()
    username = request.form['username']
    password = request.form['password']
    confirm = request.form['confirm_password']

    if username in users:
        return "Username already exists. <a href='/signup'>Try again</a>"
    if password != confirm:
        return "Passwords do not match. <a href='/signup'>Try again</a>"
    if len(password) != 8:
        return "Password must be exactly 8 characters. <a href='/signup'>Try again</a>"

    users[username] = {
        "password": password,
        "profile_pic": "default.jpg",
        "friends": [],
        "messages": {}
    }
    save_users(users)
    return redirect(url_for('login'))

@app.route('/home', methods=['POST'])
def home():
    users = load_users()
    username = request.form['username']
    password = request.form['password']
    if username in users and users[username]['password'] == password:
        session['username'] = username
        return render_template('home.html', username=username, users=users)
    return "Invalid login. <a href='/login'>Try again</a>"

@app.route('/chat_with/<friend>', methods=['GET', 'POST'])
def chat_with(friend):
    users = load_users()
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    if request.method == 'POST':
        message = request.form['message']
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        for u1, u2 in [(username, friend), (friend, username)]:
            users[u1]['messages'].setdefault(u2, []).append({
                "sender": username,
                "text": message,
                "timestamp": timestamp
            })
        save_users(users)

    messages = users[username]['messages'].get(friend, [])
    return render_template('chat.html', username=username, friend=friend, messages=messages)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# ✅ Health check route for Render
@app.route('/healthz')
def health_check():
    return "OK", 200

# ✅ Start the server
if __name__ == '__main__':
    app.run(debug=True)
