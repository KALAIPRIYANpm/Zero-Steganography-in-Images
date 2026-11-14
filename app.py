"""
DNA Image Cryptography - Flask Application
SQLite version
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from io import BytesIO
import sqlite3
import os

from config import config
from dna_utils import image_to_dna, dna_to_image, generate_dna_key
from email_utils import send_decryption_key_email, send_wrong_key_email

app = Flask(__name__)
app.config.from_object(config['development'])

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# ============================
# JINJA2 FILTERS
# ============================
@app.template_filter('strftime')
def _jinja2_filter_strftime(value, fmt='%b %d, %Y %I:%M %p'):
    """Convert ISO datetime string to formatted date string for templates.

    Usage in templates:
        {{ msg.timestamp | strftime }}
        {{ msg.timestamp | strftime('%Y-%m-%d') }}
    """
    if value is None:
        return ''
    if isinstance(value, str):
        # Handle both 'YYYY-MM-DD HH:MM:SS.ffffff' and 'YYYY-MM-DDTHH:MM:SS.ffffff'
        value = value.replace('T', ' ')
        try:
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            try:
                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return value  # Return as-is if unparseable
    return value.strftime(fmt)


# ============================
# DATABASE FUNCTIONS
# ============================
def get_db_connection():
    """Create a SQLite database connection with dict-like row access"""
    try:
        conn = sqlite3.connect(app.config['DATABASE_PATH'])
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def execute_query(query, params=None, fetch=False, fetch_one=False):
    """Execute database query.

    SQLite uses ? placeholders instead of %s.
    Returns lastrowid for INSERT, row(s) for SELECT, None on error.
    """
    # Convert any %s placeholders to ? (convenience for copy-pasted queries)
    query = query.replace('%s', '?')

    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())

        if fetch_one:
            row = cursor.fetchone()
            result = dict(row) if row else None
        elif fetch:
            rows = cursor.fetchall()
            result = [dict(r) for r in rows]
        else:
            conn.commit()
            result = cursor.lastrowid

        conn.close()
        return result

    except sqlite3.Error as e:
        print(f"Query error: {e}")
        if conn:
            conn.close()
        return None


# ============================
# HELPER FUNCTIONS
# ============================
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def get_user_by_id(user_id):
    """Get user by ID"""
    return execute_query("SELECT * FROM users WHERE id = ?", (user_id,), fetch_one=True)


def get_user_by_username(username):
    """Get user by username"""
    return execute_query("SELECT * FROM users WHERE username = ?", (username,), fetch_one=True)


# ============================
# PUBLIC ROUTES
# ============================
@app.route('/')
def home():
    """Home page"""
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        age = request.form.get('age', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Validation
        if not all([full_name, age, email, phone, username, password]):
            flash('All fields are required!', 'error')
            return redirect(url_for('register'))

        # Check if username exists
        if get_user_by_username(username):
            flash('Username already exists!', 'error')
            return redirect(url_for('register'))

        # Check if email exists
        if execute_query("SELECT id FROM users WHERE email = ?", (email,), fetch_one=True):
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))

        # Create user
        hashed_password = generate_password_hash(password)
        query = """
            INSERT INTO users (full_name, age, email, phone, username, password, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        user_id = execute_query(query, (full_name, int(age), email, phone, username,
                                        hashed_password, 1, datetime.now().isoformat()))

        if user_id:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed. Please try again.', 'error')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = get_user_by_username(username)

        if user and check_password_hash(user['password'], password):
            if not user.get('is_active', 1):
                flash('Your account has been deactivated.', 'error')
                return redirect(url_for('login'))

            session['user_id'] = user['id']
            session['username'] = user['username']

            # Update last login
            execute_query("UPDATE users SET last_login = ? WHERE id = ?",
                          (datetime.now().isoformat(), user['id']))

            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))


# ============================
# USER DASHBOARD
# ============================
@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('login'))

    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))

    # Get all users except current user
    all_users = execute_query(
        "SELECT id, username, full_name, email FROM users WHERE id != ? AND is_active = 1 ORDER BY username",
        (session['user_id'],),
        fetch=True
    ) or []

    # Get sent messages
    sent_messages = execute_query("""
        SELECT m.*, u.username as receiver_username, u.full_name as receiver_name
        FROM messages m
        JOIN users u ON m.receiver_id = u.id
        WHERE m.sender_id = ?
        ORDER BY m.timestamp DESC
    """, (session['user_id'],), fetch=True) or []

    # Get received messages
    received_messages = execute_query("""
        SELECT m.*, u.username as sender_username, u.full_name as sender_name
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.receiver_id = ?
        ORDER BY m.timestamp DESC
    """, (session['user_id'],), fetch=True) or []

    return render_template('dashboard.html',
                           user=user,
                           all_users=all_users,
                           sent_messages=sent_messages,
                           received_messages=received_messages)


@app.route('/send_message', methods=['POST'])
def send_message():
    """Send encrypted message"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    receiver_id = request.form.get('receiver_id')
    image_file = request.files.get('image')

    if not receiver_id or not image_file:
        flash('Please select receiver and image!', 'error')
        return redirect(url_for('dashboard'))

    if not allowed_file(image_file.filename):
        flash('Invalid file type!', 'error')
        return redirect(url_for('dashboard'))

    try:
        print(f"\n📤 Processing message send request...")
        print(f"👤 Sender ID: {session['user_id']}")
        print(f"👥 Receiver ID: {receiver_id}")
        print(f"📁 File: {image_file.filename}")
        print(f"📊 File size: {len(image_file.read())} bytes")
        image_file.seek(0)  # Reset file pointer after reading

        # Convert image to DNA
        dna_sequence, file_size = image_to_dna(image_file)

        print(f"🔐 DNA sequence generated successfully")
        print(f"🧬 DNA length: {len(dna_sequence)} nucleotides")
        print(f"📁 Original file size: {file_size} bytes")

        # Save message to database
        query = """
            INSERT INTO messages (sender_id, receiver_id, dna_sequence, original_filename,
                                  file_size, timestamp, is_decrypted)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        message_id = execute_query(query, (
            session['user_id'],
            receiver_id,
            dna_sequence,
            secure_filename(image_file.filename),
            file_size,
            datetime.now().isoformat(),
            0
        ))

        if message_id:
            # Generate decryption key
            decryption_key = generate_dna_key(8)

            # Save key
            execute_query("""
                INSERT INTO decryption_keys (message_id, decryption_key, email_sent, created_at)
                VALUES (?, ?, ?, ?)
            """, (message_id, decryption_key, 0, datetime.now().isoformat()))

            # Send email
            receiver = get_user_by_id(receiver_id)
            sender = get_user_by_id(session['user_id'])

            if receiver and sender:
                email_sent = send_decryption_key_email(
                    receiver['email'],
                    receiver['full_name'],
                    sender['full_name'],
                    decryption_key,
                    message_id
                )

                if email_sent:
                    execute_query("UPDATE decryption_keys SET email_sent = 1 WHERE message_id = ?",
                                  (message_id,))

            flash('Message encrypted and sent successfully!', 'success')
        else:
            flash('Failed to send message.', 'error')

    except Exception as e:
        print(f"Send message error: {e}")
        flash('Error sending message.', 'error')

    return redirect(url_for('dashboard'))


@app.route('/message/<int:message_id>')
def view_message(message_id):
    """View message"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Get message details
    message = execute_query("""
        SELECT m.*,
               s.username as sender_username, s.full_name as sender_name, s.email as sender_email,
               r.username as receiver_username, r.full_name as receiver_name, r.email as receiver_email
        FROM messages m
        JOIN users s ON m.sender_id = s.id
        JOIN users r ON m.receiver_id = r.id
        WHERE m.id = ?
    """, (message_id,), fetch_one=True)

    if not message:
        flash('Message not found!', 'error')
        return redirect(url_for('dashboard'))

    # Check if user is sender or receiver
    if message['sender_id'] != session['user_id'] and message['receiver_id'] != session['user_id']:
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))

    # Get decryption key info
    key_info = execute_query("SELECT * FROM decryption_keys WHERE message_id = ?",
                              (message_id,), fetch_one=True)

    return render_template('view_message.html', message=message, key_info=key_info)


@app.route('/decrypt/<int:message_id>', methods=['POST'])
def decrypt_message(message_id):
    """Decrypt message"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    decryption_key = request.form.get('decryption_key', '').strip().upper()

    # Get message
    message = execute_query("""
        SELECT m.*, s.email as sender_email, s.full_name as sender_name,
               r.username as receiver_username, r.full_name as receiver_name
        FROM messages m
        JOIN users s ON m.sender_id = s.id
        JOIN users r ON m.receiver_id = r.id
        WHERE m.id = ?
    """, (message_id,), fetch_one=True)

    if not message or message['receiver_id'] != session['user_id']:
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))

    if message['is_decrypted']:
        flash('Message already decrypted!', 'error')
        return redirect(url_for('view_message', message_id=message_id))

    # Get correct key
    key_info = execute_query("SELECT * FROM decryption_keys WHERE message_id = ?",
                              (message_id,), fetch_one=True)

    if not key_info:
        flash('Decryption key not found!', 'error')
        return redirect(url_for('view_message', message_id=message_id))

    # Check key
    if decryption_key == key_info['decryption_key']:
        # Correct key - decrypt
        try:
            print(f"\n🔓 Processing message decryption...")
            print(f"📨 Message ID: {message_id}")
            print(f"👤 User ID: {session['user_id']}")
            print(f"🔑 Provided key: {decryption_key}")
            print(f"🧬 DNA sequence length: {len(message['dna_sequence'])} nucleotides")

            image_bytes = dna_to_image(message['dna_sequence'])

            print(f"✅ Decryption successful!")
            print(f"🖼️  Decrypted image size: {len(image_bytes)} bytes")

            # Mark as decrypted
            execute_query("UPDATE messages SET is_decrypted = 1, decrypted_at = ? WHERE id = ?",
                          (datetime.now().isoformat(), message_id))
            execute_query("UPDATE decryption_keys SET used_at = ? WHERE message_id = ?",
                          (datetime.now().isoformat(), message_id))

            return send_file(
                BytesIO(image_bytes),
                mimetype='image/png',
                as_attachment=True,
                download_name=f"decrypted_{message['original_filename']}"
            )

        except Exception as e:
            print(f"❌ Decryption error: {e}")
            flash('Failed to decrypt image.', 'error')
    else:
        # Wrong key - log attempt
        print(f"❌ Wrong decryption key attempted for message {message_id}")
        print(f"👤 User ID: {session['user_id']}")
        print(f"🔑 Attempted key: {decryption_key}")
        print(f"🔑 Correct key: {key_info['decryption_key']}")

        execute_query("""
            INSERT INTO wrong_attempts (message_id, user_id, attempted_key, ip_address,
                                        user_agent, attempt_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (message_id, session['user_id'], decryption_key, request.remote_addr,
              request.user_agent.string, datetime.now().isoformat()))

        # Send alert to sender
        send_wrong_key_email(
            message['sender_email'],
            message['sender_name'],
            message['receiver_name'],
            request.remote_addr,
            message['receiver_username'],
            message_id
        )

        flash('Wrong decryption key!', 'error')

    return redirect(url_for('view_message', message_id=message_id))


# ============================
# ADMIN ROUTES
# ============================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = execute_query("SELECT * FROM admins WHERE username = ?", (username,), fetch_one=True)

        if admin and check_password_hash(admin['password'], password):
            session['admin_id'] = admin['id']
            session['admin_username'] = admin['username']

            execute_query("UPDATE admins SET last_login = ? WHERE id = ?",
                          (datetime.now().isoformat(), admin['id']))

            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials!', 'error')

    return render_template('admin_login_simple.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if 'admin_id' not in session:
        flash('Please login as admin!', 'error')
        return redirect(url_for('admin_login'))

    # Get statistics
    stats = {
        'total_users': 0,
        'active_users': 0,
        'total_messages': 0,
        'wrong_attempts': 0
    }

    result = execute_query("SELECT COUNT(*) as count FROM users", fetch_one=True)
    if result:
        stats['total_users'] = result['count']

    result = execute_query("SELECT COUNT(*) as count FROM users WHERE is_active = 1", fetch_one=True)
    if result:
        stats['active_users'] = result['count']

    result = execute_query("SELECT COUNT(*) as count FROM messages", fetch_one=True)
    if result:
        stats['total_messages'] = result['count']

    result = execute_query("SELECT COUNT(*) as count FROM wrong_attempts", fetch_one=True)
    if result:
        stats['wrong_attempts'] = result['count']

    # Get recent users
    recent_users = execute_query("""
        SELECT id, full_name, username, email, is_active, created_at
        FROM users
        ORDER BY created_at DESC
        LIMIT 5
    """, fetch=True) or []

    # Get recent wrong attempts
    recent_attempts = execute_query("""
        SELECT wa.*, u.username, u.full_name
        FROM wrong_attempts wa
        JOIN users u ON wa.user_id = u.id
        ORDER BY wa.attempt_time DESC
        LIMIT 5
    """, fetch=True) or []

    return render_template('admin_dashboard.html',
                           stats=stats,
                           recent_users=recent_users,
                           recent_attempts=recent_attempts)


@app.route('/admin/users')
def admin_users():
    """Manage users"""
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    users = execute_query("""
        SELECT u.*,
               (SELECT COUNT(*) FROM messages WHERE sender_id = u.id) as sent_count,
               (SELECT COUNT(*) FROM messages WHERE receiver_id = u.id) as received_count
        FROM users u
        ORDER BY u.created_at DESC
    """, fetch=True) or []

    return render_template('admin_users.html', users=users)


@app.route('/admin/user/<int:user_id>')
def admin_user_detail(user_id):
    """View user details"""
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    user = get_user_by_id(user_id)
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('admin_users'))

    # Get sent messages
    sent_messages = execute_query("""
        SELECT m.*, u.username as receiver_username, u.full_name as receiver_name
        FROM messages m
        JOIN users u ON m.receiver_id = u.id
        WHERE m.sender_id = ?
        ORDER BY m.timestamp DESC
    """, (user_id,), fetch=True) or []

    # Get received messages
    received_messages = execute_query("""
        SELECT m.*, u.username as sender_username, u.full_name as sender_name
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.receiver_id = ?
        ORDER BY m.timestamp DESC
    """, (user_id,), fetch=True) or []

    # Get wrong attempts
    wrong_attempts = execute_query("""
        SELECT wa.*, m.original_filename, s.username as sender_username
        FROM wrong_attempts wa
        JOIN messages m ON wa.message_id = m.id
        JOIN users s ON m.sender_id = s.id
        WHERE wa.user_id = ?
        ORDER BY wa.attempt_time DESC
    """, (user_id,), fetch=True) or []

    return render_template('admin_user_detail.html',
                           user=user,
                           sent_messages=sent_messages,
                           received_messages=received_messages,
                           wrong_attempts=wrong_attempts)


@app.route('/admin/user/<int:user_id>/toggle_active', methods=['POST'])
def admin_toggle_user(user_id):
    """Toggle user active status"""
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    user = get_user_by_id(user_id)
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('admin_users'))

    new_status = 0 if user.get('is_active', 1) else 1
    execute_query("UPDATE users SET is_active = ? WHERE id = ?", (new_status, user_id))

    flash(f"User {user['username']} {'activated' if new_status else 'deactivated'}.", 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
def admin_delete_user(user_id):
    """Delete user"""
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    user = get_user_by_id(user_id)
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('admin_users'))

    username = user['username']
    execute_query("DELETE FROM users WHERE id = ?", (user_id,))

    flash(f"User {username} deleted.", 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/messages')
def admin_messages():
    """View all messages"""
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    messages = execute_query("""
        SELECT m.*,
               s.username as sender_username, s.full_name as sender_name,
               r.username as receiver_username, r.full_name as receiver_name
        FROM messages m
        JOIN users s ON m.sender_id = s.id
        JOIN users r ON m.receiver_id = r.id
        ORDER BY m.timestamp DESC
    """, fetch=True) or []

    return render_template('admin_messages.html', messages=messages)


@app.route('/admin/wrong_attempts')
def admin_wrong_attempts():
    """View all wrong attempts"""
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    attempts = execute_query("""
        SELECT wa.*,
               u.username, u.full_name, u.email,
               m.original_filename, m.id as message_id,
               s.username as sender_username, s.full_name as sender_name
        FROM wrong_attempts wa
        JOIN users u ON wa.user_id = u.id
        JOIN messages m ON wa.message_id = m.id
        JOIN users s ON m.sender_id = s.id
        ORDER BY wa.attempt_time DESC
    """, fetch=True) or []

    return render_template('admin_wrong_attempts.html', attempts=attempts)


@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    flash('Admin logged out!', 'success')
    return redirect(url_for('home'))


# ============================
# RUN APPLICATION
# ============================
if __name__ == '__main__':
    print("=" * 60)
    print("DNA IMAGE CRYPTOGRAPHY SYSTEM (SQLite)")
    print("=" * 60)
    print("\n🚀 Starting application...")
    print("📍 URL: http://localhost:5000")
    print("\n⚠️  Make sure you have run create_db.py first!")
    print("\n" + "=" * 60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)