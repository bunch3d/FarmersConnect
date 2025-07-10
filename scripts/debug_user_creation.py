#!/usr/bin/env python3
"""
FarmConnect User Creation Debug Script
This script helps diagnose and fix user creation issues
"""

import sqlite3
import hashlib
import json
import traceback
from datetime import datetime
from typing import Dict, Any, Optional

class UserCreationDebugger:
    def __init__(self, db_path: str = "farmconnect.db"):
        self.db_path = db_path
        self.connection = None
    
    def connect_to_database(self) -> bool:
        """Test database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            print("✅ Database connection successful")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def check_database_structure(self) -> bool:
        """Check if users table exists and has correct structure"""
        try:
            cursor = self.connection.cursor()
            
            # Check if users table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='users'
            """)
            
            if not cursor.fetchone():
                print("❌ Users table does not exist")
                print("💡 Run the database setup script first")
                return False
            
            print("✅ Users table exists")
            
            # Check table structure
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            
            required_columns = [
                'id', 'full_name', 'email', 'password_hash', 
                'farming_experience', 'farm_type', 'location'
            ]
            
            existing_columns = [col[1] for col in columns]
            
            print("📋 Table structure:")
            for col in columns:
                print(f"   {col[1]} ({col[2]})")
            
            missing_columns = [col for col in required_columns if col not in existing_columns]
            if missing_columns:
                print(f"❌ Missing required columns: {missing_columns}")
                return False
            
            print("✅ All required columns present")
            return True
            
        except Exception as e:
            print(f"❌ Error checking database structure: {e}")
            return False
    
    def test_user_creation(self, test_data: Dict[str, str]) -> Dict[str, Any]:
        """Test creating a user with given data"""
        print(f"\n🧪 Testing user creation with data:")
        for key, value in test_data.items():
            if key == 'password':
                print(f"   {key}: {'*' * len(value)}")
            else:
                print(f"   {key}: {value}")
        
        try:
            cursor = self.connection.cursor()
            
            # Check if email already exists
            cursor.execute('SELECT email FROM users WHERE email = ?', (test_data['email'],))
            if cursor.fetchone():
                return {
                    'success': False,
                    'error': 'EMAIL_EXISTS',
                    'message': 'Email address is already registered'
                }
            
            # Hash password
            password_hash = hashlib.sha256(test_data['password'].encode()).hexdigest()
            
            # Insert user
            cursor.execute('''
                INSERT INTO users (full_name, email, password_hash, farming_experience, 
                                 farm_type, location, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                test_data['fullName'],
                test_data['email'],
                password_hash,
                test_data['farmingExperience'],
                test_data['farmType'],
                test_data['location'],
                datetime.now().isoformat()
            ))
            
            user_id = cursor.lastrowid
            self.connection.commit()
            
            print(f"✅ User created successfully with ID: {user_id}")
            
            return {
                'success': True,
                'user_id': user_id,
                'message': 'User created successfully'
            }
            
        except sqlite3.IntegrityError as e:
            error_msg = str(e)
            if 'UNIQUE constraint failed' in error_msg:
                return {
                    'success': False,
                    'error': 'UNIQUE_CONSTRAINT',
                    'message': 'Email address is already registered'
                }
            else:
                return {
                    'success': False,
                    'error': 'INTEGRITY_ERROR',
                    'message': f'Database integrity error: {error_msg}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': 'UNKNOWN_ERROR',
                'message': f'Unexpected error: {str(e)}',
                'traceback': traceback.format_exc()
            }
    
    def validate_user_data(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Validate user data before creation"""
        errors = []
        
        # Check required fields
        required_fields = ['fullName', 'email', 'password', 'farmingExperience', 'farmType', 'location']
        for field in required_fields:
            if not data.get(field) or not data[field].strip():
                errors.append(f"Field '{field}' is required")
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if data.get('email') and not re.match(email_pattern, data['email']):
            errors.append("Invalid email format")
        
        # Validate password length
        if data.get('password') and len(data['password']) < 6:
            errors.append("Password must be at least 6 characters long")
        
        # Validate farming experience
        valid_experiences = ['beginner', 'intermediate', 'experienced']
        if data.get('farmingExperience') and data['farmingExperience'] not in valid_experiences:
            errors.append(f"Invalid farming experience. Must be one of: {valid_experiences}")
        
        # Validate farm type
        valid_farm_types = ['crop', 'livestock', 'mixed', 'organic', 'hydroponics', 'other']
        if data.get('farmType') and data['farmType'] not in valid_farm_types:
            errors.append(f"Invalid farm type. Must be one of: {valid_farm_types}")
        
        if errors:
            return {
                'valid': False,
                'errors': errors
            }
        
        return {'valid': True, 'errors': []}
    
    def list_existing_users(self) -> None:
        """List existing users in the database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT id, full_name, email, farming_experience, farm_type FROM users')
            users = cursor.fetchall()
            
            if users:
                print(f"\n👥 Existing users ({len(users)}):")
                for user in users:
                    print(f"   ID: {user[0]}, Name: {user[1]}, Email: {user[2]}, Experience: {user[3]}, Type: {user[4]}")
            else:
                print("\n👥 No existing users found")
                
        except Exception as e:
            print(f"❌ Error listing users: {e}")
    
    def fix_common_issues(self) -> None:
        """Attempt to fix common database issues"""
        print("\n🔧 Attempting to fix common issues...")
        
        try:
            cursor = self.connection.cursor()
            
            # Ensure users table has all required columns
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Add missing columns if needed
            missing_columns = {
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'last_login': 'TIMESTAMP DEFAULT NULL',
                'is_mentor': 'BOOLEAN DEFAULT FALSE',
                'is_active': 'BOOLEAN DEFAULT TRUE'
            }
            
            for col_name, col_def in missing_columns.items():
                if col_name not in columns:
                    try:
                        cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")
                        print(f"✅ Added missing column: {col_name}")
                    except sqlite3.OperationalError:
                        print(f"⚠️  Column {col_name} might already exist")
            
            self.connection.commit()
            print("✅ Database structure updated")
            
        except Exception as e:
            print(f"❌ Error fixing issues: {e}")
    
    def run_comprehensive_test(self) -> None:
        """Run comprehensive user creation test"""
        print("🌱 FarmConnect User Creation Debugger")
        print("=" * 50)
        
        # Test database connection
        if not self.connect_to_database():
            return
        
        # Check database structure
        if not self.check_database_structure():
            print("\n🔧 Attempting to fix database structure...")
            self.fix_common_issues()
            if not self.check_database_structure():
                print("❌ Could not fix database structure")
                return
        
        # List existing users
        self.list_existing_users()
        
        # Test user creation with valid data
        test_user = {
            'fullName': 'Test User Debug',
            'email': f'test.debug.{int(datetime.now().timestamp())}@example.com',
            'password': 'testpassword123',
            'farmingExperience': 'beginner',
            'farmType': 'crop',
            'location': 'Test Location, USA'
        }
        
        # Validate data first
        validation = self.validate_user_data(test_user)
        if not validation['valid']:
            print(f"\n❌ Validation failed:")
            for error in validation['errors']:
                print(f"   - {error}")
            return
        
        print("\n✅ Data validation passed")
        
        # Test user creation
        result = self.test_user_creation(test_user)
        
        if result['success']:
            print(f"\n🎉 User creation test successful!")
            print(f"   User ID: {result['user_id']}")
        else:
            print(f"\n❌ User creation failed:")
            print(f"   Error: {result['error']}")
            print(f"   Message: {result['message']}")
            if 'traceback' in result:
                print(f"   Traceback: {result['traceback']}")
        
        # Close connection
        if self.connection:
            self.connection.close()

def main():
    """Main function to run the debugger"""
    debugger = UserCreationDebugger()
    debugger.run_comprehensive_test()

if __name__ == "__main__":
    main()
