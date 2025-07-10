from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import sqlite3
import hashlib
import re
import traceback
from datetime import datetime
from typing import Dict, Any

class FixedFarmConnectHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """Override to add timestamps to logs"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {format % args}")
    
    def do_POST(self):
        """Handle POST requests with better error handling"""
        self.log_message(f"POST request to: {self.path}")
        
        if self.path == '/signup':
            self.handle_signup_with_debugging()
        elif self.path == '/signin':
            self.handle_signin()
        elif self.path == '/debug/test-db':
            self.handle_database_test()
        else:
            self.send_error(404, "Not Found")
    
    def do_GET(self):
        """Handle GET requests for debugging"""
        if self.path == '/debug/users':
            self.handle_list_users()
        elif self.path == '/debug/db-info':
            self.handle_database_info()
        else:
            self.send_error(404, "Not Found")
    
    def handle_signup_with_debugging(self):
        """Enhanced signup handler with comprehensive debugging"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            # Parse form data
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            # Extract and clean form fields
            signup_data = {}
            for key in ['fullName', 'email', 'password', 'confirmPassword', 
                       'farmingExperience', 'farmType', 'location']:
                value = form_data.get(key, [''])[0].strip()
                signup_data[key] = value
            
            self.log_message(f"Signup attempt for: {signup_data.get('email', 'unknown')}")
            self.log_message(f"Form fields received: {list(signup_data.keys())}")
            
            # Step 1: Validate input data
            validation_result = self.validate_signup_data(signup_data)
            if not validation_result['valid']:
                self.log_message(f"Validation failed: {validation_result['message']}")
                self.send_json_response({
                    "success": False,
                    "error": "VALIDATION_ERROR",
                    "message": validation_result['message'],
                    "debug_info": {
                        "step": "validation",
                        "received_fields": list(signup_data.keys()),
                        "validation_errors": validation_result.get('errors', [])
                    }
                })
                return
            
            # Step 2: Check database connection
            db_check = self.check_database_connection()
            if not db_check['success']:
                self.log_message(f"Database connection failed: {db_check['message']}")
                self.send_json_response({
                    "success": False,
                    "error": "DATABASE_CONNECTION_ERROR",
                    "message": "Could not connect to database",
                    "debug_info": {
                        "step": "database_connection",
                        "error": db_check['message']
                    }
                })
                return
            
            # Step 3: Check database structure
            structure_check = self.check_database_structure()
            if not structure_check['success']:
                self.log_message(f"Database structure issue: {structure_check['message']}")
                # Try to fix the structure
                fix_result = self.fix_database_structure()
                if not fix_result['success']:
                    self.send_json_response({
                        "success": False,
                        "error": "DATABASE_STRUCTURE_ERROR",
                        "message": "Database structure is invalid and could not be fixed",
                        "debug_info": {
                            "step": "database_structure",
                            "error": structure_check['message'],
                            "fix_attempted": True,
                            "fix_result": fix_result['message']
                        }
                    })
                    return
            
            # Step 4: Create user
            user_result = self.create_user_in_database(signup_data)
            
            if user_result['success']:
                self.log_message(f"User created successfully: {signup_data['email']}")
                self.send_json_response({
                    "success": True,
                    "message": "Account created successfully!",
                    "user": user_result['user'],
                    "debug_info": {
                        "step": "user_creation",
                        "user_id": user_result['user']['id']
                    }
                })
            else:
                self.log_message(f"User creation failed: {user_result['message']}")
                self.send_json_response({
                    "success": False,
                    "error": user_result.get('error', 'USER_CREATION_ERROR'),
                    "message": user_result['message'],
                    "debug_info": {
                        "step": "user_creation",
                        "error_details": user_result.get('details', 'No additional details')
                    }
                })
            
        except Exception as e:
            error_msg = f"Unexpected server error: {str(e)}"
            self.log_message(f"Exception in signup: {error_msg}")
            self.log_message(f"Traceback: {traceback.format_exc()}")
            
            self.send_json_response({
                "success": False,
                "error": "SERVER_ERROR",
                "message": "An unexpected error occurred",
                "debug_info": {
                    "step": "exception_handling",
                    "error": error_msg,
                    "traceback": traceback.format_exc()
                }
            })
    
    def validate_signup_data(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Enhanced validation with detailed error reporting"""
        errors = []
        
        # Check required fields
        required_fields = {
            'fullName': 'Full Name',
            'email': 'Email Address',
            'password': 'Password',
            'confirmPassword': 'Confirm Password',
            'farmingExperience': 'Farming Experience',
            'farmType': 'Farm Type',
            'location': 'Location'
        }
        
        for field, display_name in required_fields.items():
            if not data.get(field):
                errors.append(f"{display_name} is required")
        
        # If basic fields are missing, return early
        if errors:
            return {
                'valid': False,
                'message': 'Required fields are missing',
                'errors': errors
            }
        
        # Validate full name
        if len(data['fullName']) < 2:
            errors.append('Full name must be at least 2 characters long')
        elif len(data['fullName']) > 100:
            errors.append('Full name is too long (max 100 characters)')
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            errors.append('Please enter a valid email address')
        
        # Validate password
        password = data['password']
        if len(password) < 6:
            errors.append('Password must be at least 6 characters long')
        elif len(password) > 128:
            errors.append('Password is too long (max 128 characters)')
        
        # Check password confirmation
        if password != data['confirmPassword']:
            errors.append('Passwords do not match')
        
        # Validate farming experience
        valid_experiences = ['beginner', 'intermediate', 'experienced']
        if data['farmingExperience'] not in valid_experiences:
            errors.append(f'Invalid farming experience. Must be one of: {", ".join(valid_experiences)}')
        
        # Validate farm type
        valid_farm_types = ['crop', 'livestock', 'mixed', 'organic', 'hydroponics', 'other']
        if data['farmType'] not in valid_farm_types:
            errors.append(f'Invalid farm type. Must be one of: {", ".join(valid_farm_types)}')
        
        # Validate location
        if len(data['location']) < 3:
            errors.append('Location must be at least 3 characters long')
        elif len(data['location']) > 255:
            errors.append('Location is too long (max 255 characters)')
        
        if errors:
            return {
                'valid': False,
                'message': '; '.join(errors),
                'errors': errors
            }
        
        return {'valid': True, 'message': 'Validation passed'}
    
    def check_database_connection(self) -> Dict[str, Any]:
        """Check if database connection works"""
        try:
            conn = sqlite3.connect('farmconnect.db')
            conn.close()
            return {'success': True, 'message': 'Database connection successful'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def check_database_structure(self) -> Dict[str, Any]:
        """Check if database has correct structure"""
        try:
            conn = sqlite3.connect('farmconnect.db')
            cursor = conn.cursor()
            
            # Check if users table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='users'
            """)
            
            if not cursor.fetchone():
                conn.close()
                return {'success': False, 'message': 'Users table does not exist'}
            
            # Check table structure
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            required_columns = ['id', 'full_name', 'email', 'password_hash', 
                              'farming_experience', 'farm_type', 'location']
            
            missing_columns = [col for col in required_columns if col not in column_names]
            
            conn.close()
            
            if missing_columns:
                return {
                    'success': False, 
                    'message': f'Missing required columns: {", ".join(missing_columns)}'
                }
            
            return {'success': True, 'message': 'Database structure is correct'}
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def fix_database_structure(self) -> Dict[str, Any]:
        """Attempt to fix database structure"""
        try:
            conn = sqlite3.connect('farmconnect.db')
            cursor = conn.cursor()
            
            # Create users table if it doesn't exist
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
                    last_login TIMESTAMP DEFAULT NULL,
                    is_mentor BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'Database structure fixed'}
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def create_user_in_database(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Create user with enhanced error handling"""
        conn = None
        try:
            conn = sqlite3.connect('farmconnect.db')
            cursor = conn.cursor()
            
            # Check if email already exists
            cursor.execute('SELECT email FROM users WHERE email = ?', (data['email'],))
            if cursor.fetchone():
                return {
                    'success': False,
                    'error': 'EMAIL_EXISTS',
                    'message': 'Email address is already registered',
                    'details': f'Email {data["email"]} already exists in database'
                }
            
            # Hash password
            password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
            
            # Insert user
            cursor.execute('''
                INSERT INTO users (full_name, email, password_hash, farming_experience, 
                                 farm_type, location, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['fullName'],
                data['email'],
                password_hash,
                data['farmingExperience'],
                data['farmType'],
                data['location'],
                datetime.now().isoformat()
            ))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            # Return user data
            user_data = {
                'id': user_id,
                'full_name': data['fullName'],
                'email': data['email'],
                'farming_experience': data['farmingExperience'],
                'farm_type': data['farmType'],
                'location': data['location'],
                'is_mentor': False,
                'created_at': datetime.now().isoformat()
            }
            
            return {
                'success': True,
                'user': user_data,
                'message': 'User created successfully'
            }
            
        except sqlite3.IntegrityError as e:
            error_msg = str(e)
            if 'UNIQUE constraint failed' in error_msg:
                return {
                    'success': False,
                    'error': 'EMAIL_EXISTS',
                    'message': 'Email address is already registered',
                    'details': error_msg
                }
            else:
                return {
                    'success': False,
                    'error': 'INTEGRITY_ERROR',
                    'message': 'Database integrity constraint violation',
                    'details': error_msg
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': 'DATABASE_ERROR',
                'message': 'Database operation failed',
                'details': str(e)
            }
        
        finally:
            if conn:
                conn.close()
    
    def handle_database_test(self):
        """Handle database test endpoint"""
        try:
            conn = sqlite3.connect('farmconnect.db')
            cursor = conn.cursor()
            
            # Get database info
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            self.send_json_response({
                "success": True,
                "database_info": {
                    "user_count": user_count,
                    "tables": tables,
                    "database_file": "farmconnect.db"
                }
            })
            
        except Exception as e:
            self.send_json_response({
                "success": False,
                "error": str(e)
            })
    
    def handle_list_users(self):
        """Handle list users endpoint"""
        try:
            conn = sqlite3.connect('farmconnect.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, full_name, email, farming_experience, farm_type, created_at
                FROM users ORDER BY created_at DESC LIMIT 10
            ''')
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    'id': row[0],
                    'full_name': row[1],
                    'email': row[2],
                    'farming_experience': row[3],
                    'farm_type': row[4],
                    'created_at': row[5]
                })
            
            conn.close()
            
            self.send_json_response({
                "success": True,
                "users": users,
                "count": len(users)
            })
            
        except Exception as e:
            self.send_json_response({
                "success": False,
                "error": str(e)
            })
    
    def handle_database_info(self):
        """Handle database info endpoint"""
        try:
            conn = sqlite3.connect('farmconnect.db')
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            
            # Get user count
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            conn.close()
            
            self.send_json_response({
                "success": True,
                "database_info": {
                    "table_columns": [{"name": col[1], "type": col[2]} for col in columns],
                    "user_count": user_count
                }
            })
            
        except Exception as e:
            self.send_json_response({
                "success": False,
                "error": str(e)
            })
    
    def handle_signin(self):
        """Handle signin (existing functionality)"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            email = form_data.get('email', [''])[0].strip()
            password = form_data.get('password', [''])[0].strip()
            
            # Authenticate user
            auth_result = self.authenticate_user(email, password)
            self.send_json_response(auth_result)
            
        except Exception as e:
            self.send_json_response({
                "success": False,
                "error": "SIGNIN_ERROR",
                "message": f"Sign-in error: {str(e)}"
            })
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user credentials"""
        try:
            conn = sqlite3.connect('farmconnect.db')
            cursor = conn.cursor()
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            cursor.execute('''
                SELECT id, full_name, email, farming_experience, farm_type, 
                       location, is_mentor, created_at
                FROM users 
                WHERE email = ? AND password_hash = ?
            ''', (email, password_hash))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                user_data = {
                    'id': user[0],
                    'full_name': user[1],
                    'email': user[2],
                    'farming_experience': user[3],
                    'farm_type': user[4],
                    'location': user[5],
                    'is_mentor': bool(user[6]),
                    'created_at': user[7]
                }
                
                return {'success': True, 'user': user_data}
            else:
                return {'success': False, 'message': 'Invalid email or password'}
                
        except Exception as e:
            return {'success': False, 'message': f'Authentication error: {str(e)}'}
    
    def send_json_response(self, data: Dict[str, Any]):
        """Send JSON response with proper headers"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2)
        self.log_message(f"Sending response: {response_json[:200]}...")
        self.wfile.write(response_json.encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_server(port=8000):
    """Run the enhanced server with debugging"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, FixedFarmConnectHandler)
    
    print("🌱 FarmConnect Enhanced Debug Server")
    print("=" * 50)
    print(f"🚀 Server running on port {port}")
    print(f"🌐 Main site: http://localhost:{port}")
    print(f"🔧 Debug endpoints:")
    print(f"   - GET  /debug/users     - List users")
    print(f"   - GET  /debug/db-info   - Database info")
    print(f"   - POST /debug/test-db   - Test database")
    print("=" * 50)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        httpd.server_close()

if __name__ == "__main__":
    # Initialize database
    import os
    if not os.path.exists('farmconnect.db'):
        print("⚠️  Database file not found. Creating basic structure...")
        conn = sqlite3.connect('farmconnect.db')
        cursor = conn.cursor()
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
                last_login TIMESTAMP DEFAULT NULL,
                is_mentor BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ Basic database structure created")
    
    run_server()
