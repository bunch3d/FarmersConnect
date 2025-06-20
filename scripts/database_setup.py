import sqlite3
import hashlib
from datetime import datetime

def create_database():
    """Create the database and tables for the farming community website"""
    conn = sqlite3.connect('farmconnect.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            farming_experience TEXT NOT NULL,
            farm_type TEXT NOT NULL,
            location TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_mentor BOOLEAN DEFAULT FALSE,
            profile_image TEXT DEFAULT NULL
        )
    ''')
    
    # Posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            likes_count INTEGER DEFAULT 0,
            comments_count INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Comments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Likes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            post_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, post_id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (post_id) REFERENCES posts (id)
        )
    ''')
    
    # Mentorship table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mentorships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mentor_id INTEGER NOT NULL,
            mentee_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (mentor_id) REFERENCES users (id),
            FOREIGN KEY (mentee_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database and tables created successfully!")

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def seed_sample_data():
    """Add sample data to the database"""
    conn = sqlite3.connect('farmconnect.db')
    cursor = conn.cursor()
    
    # Sample users
    sample_users = [
        ('John Davis', 'john.davis@email.com', hash_password('password123'), 'experienced', 'organic', 'Iowa, USA', True),
        ('Sarah Martinez', 'sarah.martinez@email.com', hash_password('password123'), 'beginner', 'crop', 'California, USA', False),
        ('Robert Brown', 'robert.brown@email.com', hash_password('password123'), 'experienced', 'mixed', 'Texas, USA', True),
        ('Linda Wilson', 'linda.wilson@email.com', hash_password('password123'), 'experienced', 'livestock', 'Texas, USA', True),
        ('Michael Johnson', 'michael.johnson@email.com', hash_password('password123'), 'experienced', 'organic', 'Iowa, USA', True),
    ]
    
    cursor.executemany('''
        INSERT INTO users (full_name, email, password_hash, farming_experience, farm_type, location, is_mentor)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', sample_users)
    
    # Sample posts
    sample_posts = [
        (1, 'Best practices for organic pest control?', 'I\'ve been transitioning to organic farming and looking for effective, natural pest control methods. What has worked best for you?', 'organic'),
        (2, 'First-time farmer seeking advice on soil preparation', 'Hi everyone! I just bought my first piece of land and I\'m excited to start farming. The soil test results show low nitrogen levels.', 'crops'),
        (3, 'Weather patterns affecting crop yields this season', 'Has anyone else noticed unusual weather patterns this growing season? My corn yields are down 15% compared to last year.', 'weather'),
    ]
    
    cursor.executemany('''
        INSERT INTO posts (user_id, title, content, category)
        VALUES (?, ?, ?, ?)
    ''', sample_posts)
    
    conn.commit()
    conn.close()
    print("Sample data added successfully!")

if __name__ == "__main__":
    create_database()
    seed_sample_data()
