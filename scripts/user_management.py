import sqlite3
import hashlib
from datetime import datetime

class UserManager:
    def __init__(self, db_path='farmconnect.db'):
        self.db_path = db_path
    
    def hash_password(self, password):
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, full_name, email, password, farming_experience, farm_type, location):
        """Create a new user account"""
        conn = sqlite3.connect("self.db_path") #self.db_path
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (full_name, email, password_hash, farming_experience, farm_type, location)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (full_name, email, password_hash, farming_experience, farm_type, location))
            
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            
            print(f"User {full_name} created successfully with ID: {user_id}")
            return {"success": True, "user_id": user_id, "message": "Account created successfully!"}
            
        except sqlite3.IntegrityError:
            conn.close()
            return {"success": False, "message": "Email already exists!"}
        except Exception as e:
            conn.close()
            return {"success": False, "message": f"Error creating account: {str(e)}"}
    
    def authenticate_user(self, email, password):
        """Authenticate a user login"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute('''
            SELECT id, full_name, email, farming_experience, farm_type, location, is_mentor
            FROM users 
            WHERE email = ? AND password_hash = ?
        ''', (email, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        if user:
            return {
                "success": True,
                "user": {
                    "id": user[0],
                    "full_name": user[1],
                    "email": user[2],
                    "farming_experience": user[3],
                    "farm_type": user[4],
                    "location": user[5],
                    "is_mentor": user[6]
                }
            }
        else:
            return {"success": False, "message": "Invalid email or password!"}
        conn.close()

    def get_user_profile(self, user_id):
        """Get user profile information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, full_name, email, farming_experience, farm_type, location, is_mentor, created_at
            FROM users 
            WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                "success": True,
                "user": {
                    "id": user[0],
                    "full_name": user[1],
                    "email": user[2],
                    "farming_experience": user[3],
                    "farm_type": user[4],
                    "location": user[5],
                    "is_mentor": user[6],
                    "created_at": user[7]
                }
            }
        else:
            return {"success": False, "message": "User not found!"}

# Example usage
if __name__ == "__main__":
    user_manager = UserManager()
    
    # Test user creation
    result = user_manager.create_user(
        "Test User",
        "test@example.com",
        "testpassword",
        "beginner",
        "crop",
        "Test Location"
    )
    print("Create user result:", result)
    
    # Test authentication
    auth_result = user_manager.authenticate_user("test@example.com", "testpassword")
    print("Authentication result:", auth_result)
