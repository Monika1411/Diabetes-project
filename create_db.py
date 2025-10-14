from app import db, app
import sqlite3

with app.app_context():
    # Create tables if they don't exist
    db.create_all()
    print("Tables checked/created successfully!")

    # Add 'name' column if it doesn't exist
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Check if 'name' column exists
    cursor.execute("PRAGMA table_info(user);")
    columns = [col[1] for col in cursor.fetchall()]
    if 'name' not in columns:
        cursor.execute("ALTER TABLE user ADD COLUMN name TEXT;")
        print("Added 'name' column to user table.")

    conn.commit()
    conn.close()
    print("Database ready!")
