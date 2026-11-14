"""
Database Creation Script for DNA Image Cryptography System
SQLite version - no server required
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dna_image_crypto.db')


def get_connection():
    """Get a database connection with row_factory for dict-like access"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables():
    """Create all tables"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # USERS TABLE
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            last_login TEXT NULL
        )
        """)


        # MESSAGES TABLE
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            dna_sequence TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            is_decrypted INTEGER DEFAULT 0,
            decrypted_at TEXT NULL,
            FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)

        # DECRYPTION KEYS TABLE
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS decryption_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL UNIQUE,
            decryption_key TEXT NOT NULL,
            email_sent INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            used_at TEXT NULL,
            FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
        )
        """)

        # WRONG ATTEMPTS TABLE
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS wrong_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            attempted_key TEXT NOT NULL,
            ip_address TEXT NOT NULL,
            user_agent TEXT,
            attempt_time TEXT NOT NULL,
            FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)

        # ADMINS TABLE
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_login TEXT NULL
        )
        """)

        conn.commit()
        conn.close()

        print("✓ All tables created successfully")
        return True

    except sqlite3.Error as e:
        print(f"✗ Error creating tables: {e}")
        return False


def insert_test_data():
    """Insert test users and admin"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Create test users
        test_users = [
            ('Alice Johnson', 25, 'alice@example.com', '1234567890', 'alice', 'password123'),
            ('Bob Smith', 30, 'bob@example.com', '9876543210', 'bob', 'password123'),
            ('Charlie Brown', 28, 'charlie@example.com', '5551234567', 'charlie', 'password123')
        ]

        for full_name, age, email, phone, username, password in test_users:
            hashed_password = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO users (full_name, age, email, phone, username, password, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (full_name, age, email, phone, username, hashed_password, 1, datetime.now().isoformat()))

        # Create admin
        admin_password = generate_password_hash('admin123')
        cursor.execute("""
            INSERT INTO admins (username, password, created_at)
            VALUES (?, ?, ?)
        """, ('admin', admin_password, datetime.now().isoformat()))

        conn.commit()
        conn.close()

        print("\n✓ Test data created successfully")
        print("\n📝 Test User Credentials:")
        print("   alice / password123")
        print("   bob / password123")
        print("   charlie / password123")
        print("\n📝 Admin Credentials:")
        print("   admin / admin123")

        return True

    except sqlite3.Error as e:
        print(f"✗ Error inserting test data: {e}")
        return False


def verify_database():
    """Verify database setup"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("\n" + "=" * 60)
        print("DATABASE VERIFICATION")
        print("=" * 60)

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("\n📊 Tables Created:")
        for table in tables:
            print(f"   ✓ {table[0]}")

        cursor.execute("SELECT COUNT(*) FROM users")
        print(f"\n👥 Users: {cursor.fetchone()[0]}")

        cursor.execute("SELECT COUNT(*) FROM admins")
        print(f"👤 Admins: {cursor.fetchone()[0]}")

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"✗ Error verifying database: {e}")
        return False


def main():
    print("=" * 60)
    print("DNA IMAGE CRYPTOGRAPHY - DATABASE SETUP (SQLite)")
    print("=" * 60)
    print(f"\n📂 Database file: {DB_PATH}")

    # Remove existing DB for a clean setup
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("✓ Removed existing database for clean setup")

    print("\n🔧 Step 1: Creating tables...")
    if not create_tables():
        return

    print("\n🔧 Step 2: Inserting test data...")
    if not insert_test_data():
        return

    print("\n🔧 Step 3: Verifying database...")
    verify_database()

    print("\n" + "=" * 60)
    print("✓ DATABASE SETUP COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print("\n🚀 Next Steps:")
    print("   1. Run: python app.py")
    print("   2. Open: http://localhost:5000")
    print("   3. Login with test credentials above")

if __name__ == "__main__":
    main()