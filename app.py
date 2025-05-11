# Import necessary modules
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import json
import re
from flask_mail import Mail, Message

# Initialize the Flask application
app = Flask(__name__)

# SQLite database file name
DB_NAME = 'users.db'
DATABASE = 'users.db'

# Email server configuration for password reset and other notifications
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'ana.kopadze31@gmail.com'  # Sender's email
app.config['MAIL_PASSWORD'] = 'flsngmjdvkzgaxsi'          # App-specific password
app.config['MAIL_DEFAULT_SENDER'] = 'ana.kopadze31@gmail.com'
mail = Mail(app)

# Secret key for sessions and CSRF protection
app.secret_key = 'your_secret_key_here'

# Route to verify email sending functionality
@app.route('/test-email')
def test_email():
    try:
        msg = Message('Test Email from Therooms',
                      recipients=['ana.kopadze31@gmail.com'])
        msg.body = 'This is a test email sent from your Flask app.'
        mail.send(msg)
        return 'Test email sent successfully!'
    except Exception as e:
        return f'Error sending email: {str(e)}'

# Create tables in the database if they don't already exist
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Table for users
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # Table for rooms associated with users
    c.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            room_name TEXT NOT NULL,
            grid_data TEXT DEFAULT '{}',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')

    conn.commit()
    conn.close()

# Default route redirects users based on login status
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

# Route to handle user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        email = request.form['email']
        password = request.form['password']
        
        # Look up the user in the database
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT id, password FROM users WHERE email=?", (email,))
        user = c.fetchone()
        conn.close()

        # Validate credentials
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]

            # Get admin status
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT is_admin FROM users WHERE id=?", (user[0],))
            is_admin = c.fetchone()[0]
            conn.close()

            session['is_admin'] = is_admin
            return redirect(url_for('home'))

        flash('Invalid email or password.')
    return render_template('login.html')

# Route to handle user registration
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            flash('Invalid email format. Please enter a valid email address.', 'error')
            return redirect(url_for('signup'))

        # Check if user already exists
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
        existing_user = cursor.fetchone()
        conn.close()

        if existing_user:
            flash('Username or email is already taken.', 'error')
            return redirect(url_for('signup'))

        # Store new user with hashed password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)",
                       (email, username, hashed_password))
        conn.commit()
        conn.close()

        flash('You have successfully signed up!', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

# Route to handle password reset email
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        # Check if email exists
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT id, email FROM users WHERE email=?", (email,))
        user = c.fetchone()
        conn.close()

        if user:
            # Send reset link via email
            reset_link = f'http://127.0.0.1:5001/reset-password/{user[0]}'
            msg = Message("Password Reset Request",
                          recipients=[email],
                          body=f"Click on the following link to reset your password: {reset_link}")
            mail.send(msg)
            flash('Password reset instructions have been sent.')
        else:
            flash('Email not found.')

        return redirect(url_for('login'))

    return render_template('forgot_password.html')

# Route to reset password using user ID
@app.route('/reset-password/<int:user_id>', methods=['GET', 'POST'])
def reset_password(user_id):
    if request.method == 'POST':
        new_password = request.form['new_password']
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

        # Update password in database
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("UPDATE users SET password=? WHERE id=?", (hashed_password, user_id))
        conn.commit()
        conn.close()

        flash('Your password has been updated!')
        return redirect(url_for('login'))

    return render_template('reset_password.html')

# Admin route to view all registered users
@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Check if current user is admin
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT is_admin FROM users WHERE id = ?", (session['user_id'],))
    result = c.fetchone()

    if not result or result[0] != 1:
        conn.close()
        flash('You do not have admin access.', 'danger')
        return redirect(url_for('home'))

    # Get list of all users
    c.execute("SELECT id, email, username, created_at FROM users")
    users = c.fetchall()
    conn.close()

    return render_template('admin_users.html', users=users)

# Admin route to update user info
@app.route('/admin/edit_user/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Check admin rights
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT is_admin FROM users WHERE id = ?", (session['user_id'],))
    result = c.fetchone()

    if not result or result[0] != 1:
        conn.close()
        flash('You do not have admin access.', 'danger')
        return redirect(url_for('home'))

    new_email = request.form.get('email')
    new_username = request.form.get('username')

    if not new_email or not new_username:
        flash('Email and username are required.', 'error')
        return redirect(url_for('admin_users'))

    # Validate email format
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, new_email):
        flash('Invalid email format.', 'error')
        return redirect(url_for('admin_users'))

    c.execute("UPDATE users SET email = ?, username = ? WHERE id = ?", (new_email, new_username, user_id))
    conn.commit()
    conn.close()

    flash('User updated successfully!', 'success')
    return redirect(url_for('admin_users'))

# Admin route to delete a user
@app.route('/admin/delete/<int:user_id>', methods=['GET'])
def delete_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Check admin status
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT is_admin FROM users WHERE id = ?", (session['user_id'],))
    result = c.fetchone()

    if not result or result[0] != 1:
        conn.close()
        flash('You do not have admin access.', 'danger')
        return redirect(url_for('home'))

    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin_users'))

# Route for a user to delete their own account
@app.route('/delete-account', methods=['GET'])
def delete_account():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM rooms WHERE user_id=?", (user_id,))
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    session.clear()
    flash('Your account has been deleted.', 'success')
    return redirect(url_for('index'))

# Route for user's home page after login
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Fetch user details
    c.execute("SELECT username, email FROM users WHERE id=?", (session['user_id'],))
    username, email = c.fetchone()

    # Fetch rooms created by user
    c.execute("SELECT id, room_name FROM rooms WHERE user_id=?", (session['user_id'],))
    rooms = c.fetchall()
    conn.close()

    return render_template('home.html', username=username, email=email, rooms=rooms, is_admin=session.get('is_admin', 0))

# Route to update user profile
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    username = request.form['username']
    email = request.form['email']

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET username=?, email=? WHERE id=?", (username, email, session['user_id']))
    conn.commit()
    conn.close()

    return redirect(url_for('home'))

# Route to create a new room
@app.route('/create_room', methods=['POST'])
def create_room():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    room_name = request.form.get('room_name')
    user_id = session['user_id']

    if room_name:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO rooms (user_id, room_name) VALUES (?, ?)", (user_id, room_name))
        conn.commit()
        conn.close()

    return redirect(url_for('home'))

# Route to edit a room
@app.route('/edit_room/<int:room_id>', methods=['GET', 'POST'])
def edit_room(room_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT room_name, grid_data FROM rooms WHERE id=?", (room_id,))
    room = c.fetchone()
    conn.close()

    if room is None:
        flash("Room not found.", "danger")
        return redirect(url_for('home'))

    room_name = room[0]

    try:
        layout_data = json.loads(room[1]) if room[1] else []
    except Exception as e:
        layout_data = []

    return render_template('edit_room.html', room_name=room_name, room_id=room_id, grid_data=layout_data)

# Route to delete a room
@app.route('/delete_room/<int:room_id>', methods=['POST'])
def delete_room(room_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id FROM rooms WHERE id=?", (room_id,))
    room = c.fetchone()

    # Ensure the room belongs to the current user
    if room and room[0] == session['user_id']:
        c.execute("DELETE FROM rooms WHERE id=?", (room_id,))
        conn.commit()
    conn.close()

    return redirect(url_for('home'))

# Route to save room layout data (JSON format)
@app.route('/save_room/<int:room_id>', methods=['POST'])
def save_room(room_id):
    try:
        data = request.get_json()
        layout = json.dumps(data['layout'])

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE rooms
            SET grid_data = ?, updated_at = datetime('now')
            WHERE id = ?
        """, (layout, room_id))
        conn.commit()
        conn.close()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Route to log out the user
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Route to rename a room
@app.route('/rename_room/<int:room_id>', methods=['POST'])
def rename_room(room_id):
    if 'user_id' not in session:
        return jsonify(success=False, error="Not logged in")

    data = request.json
    new_name = data.get('new_name', '').strip()

    if not new_name:
        return jsonify(success=False, error="No name provided")

    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("UPDATE rooms SET room_name = ?, updated_at = datetime('now') WHERE id = ? AND user_id = ?", 
                  (new_name, room_id, session['user_id']))
        conn.commit()
        conn.close()

        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

# Start the Flask app and initialize the database
if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)
