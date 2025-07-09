from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import sqlite3
import hashlib
import re
from datetime import datetime
from typing import Dict, Any

class FarmConnectSignupHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle POST requests"""
        print(f"Received POST request to: {self.path}")
        
        if self.path == '/signup':
            self.handle_signup()
        elif self.path == '/signin':
            self.handle_signin()
        else:
            self.send_error(404, "Not Found")
    
    def handle_signup(self):
        """Handle user signup with comprehensive validation"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            # Parse the form data from frontend
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            # Extract form fields
            signup_data = {
                'fullName': self.get_form_field(form_data, 'fullName'),
                'email': self.get_form_field(form_data, 'email'),
                'password': self.get_form_field(form_data, 'password'),
                'confirmPassword': self.get_form_field(form_data, 'confirmPassword'),
                'farmingExperience': self.get_form_field(form_data, 'farmingExperience'),
                'farmType': self.get_form_field(form_data, 'farmType'),
                'location': self.get_form_field(form_data, 'location')
            }
            
            print(f"📝 Signup attempt for: {signup_data['email']}")
            print(f"📊 Form data received: {list(signup_data.keys())}")
            
            # Validate the signup data
            validation_result = self.validate_signup_data(signup_data)
            if not validation_result['valid']:
                print(f"❌ Validation failed: {validation_result['message']}")
                self.send_json_response({
                    "success": False, 
                    "message": validation_result['message']
                })
                return
            
            # Create user in database
            user_result = self.create_user_in_database(signup_data)
            
            if user_result['success']:
                print(f"✅ User {signup_data['email']} created successfully")
                
                # Log the successful signup
                self.log_user_activity(user_result['user']['id'], 'signup', {
                    'email': signup_data['email'],
                    'farming_experience': signup_data['farmingExperience'],
                    'farm_type': signup_data['farmType']
                })
                
                # Send success response with user data
                self.send_json_response({
                    "success": True,
                    "message": "Account created successfully!",
                    "user": user_result['user']
                })
            else:
                print(f"❌ Database error: {user_result['message']}")
                self.send_json_response({
                    "success": False,
                    "message": user_result['message']
                })
            
        except Exception as e:
            error_msg = f"Server error during signup: {str(e)}"
            print(f"💥 {error_msg}")
            self.send_json_response({
                "success": False, 
                "message": "An unexpected error occurred. Please try again."
            })
    
    def get_form_field(self, form_data: dict, field_name: str) -> str:
        """Safely extract form field value"""
        return form_data.get(field_name, [''])[0].strip()
    
    def validate_signup_data(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Comprehensive validation of signup data"""
        
        # Check required fields
        required_fields = ['fullName', 'email', 'password', 'confirmPassword', 
                          'farmingExperience', 'farmType', 'location']
        
        for field in required_fields:
            if not data.get(field):
                return {
                    'valid': False, 
                    'message': f'{field.replace("_", " ").title()} is required'
                }
        
        # Validate full name
        if len(data['fullName']) < 2:
            return {'valid': False, 'message': 'Full name must be at least 2 characters long'}
        
        if len(data['fullName']) > 100:
            return {'valid': False, 'message': 'Full name is too long (max 100 characters)'}
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return {'valid': False, 'message': 'Please enter a valid email address'}
        
        # Validate password strength
        password = data['password']
        if len(password) < 6:
            return {'valid': False, 'message': 'Password must be at least 6 characters long'}
        
        if len(password) > 128:
            return {'valid': False, 'message': 'Password is too long (max 128 characters)'}
        
        # Check password confirmation
        if password != data['confirmPassword']:
            return {'valid': False, 'message': 'Passwords do not match'}
        
        # Validate farming experience
        valid_experiences = ['beginner', 'intermediate', 'experienced']
        if data['farmingExperience'] not in valid_experiences:
            return {'valid': False, 'message': 'Please select a valid farming experience level'}
        
        # Validate farm type
        valid_farm_types = ['crop', 'livestock', 'mixed', 'organic', 'hydroponics', 'other']
        if data['farmType'] not in valid_farm_types:
            return {'valid': False, 'message': 'Please select a valid farm type'}
        
        # Validate location
        if len(data['location']) < 3:
            return {'valid': False, 'message': 'Location must be at least 3 characters long'}
        
        if len(data['location']) > 255:
            return {'valid': False, 'message': 'Location is too long (max 255 characters)'}
        
        return {'valid': True, 'message': 'Validation passed'}
    
    def create_user_in_database(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Create user in SQLite database"""
        conn = sqlite3.connect('farmconnect.db')
        cursor = conn.cursor()
        
        try:
            # Check if email already exists
            cursor.execute('SELECT email FROM users WHERE email = ?', (data['email'],))
            if cursor.fetchone():
                return {'success': False, 'message': 'Email address is already registered'}
            
            # Hash the password
            password_hash = self.hash_password(data['password'])
            
            # Insert new user
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
            
            # Return user data (without password hash)
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
            
            return {'success': True, 'user': user_data}
            
        except sqlite3.IntegrityError as e:
            return {'success': False, 'message': 'Email address is already registered'}
        except Exception as e:
            return {'success': False, 'message': f'Database error: {str(e)}'}
        finally:
            conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256 (upgrade to bcrypt in production)"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def handle_signin(self):
        """Handle user signin (existing functionality)"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            email = self.get_form_field(form_data, 'email')
            password = self.get_form_field(form_data, 'password')
            
            print(f"🔐 Sign-in attempt for: {email}")
            
            # Authenticate user
            auth_result = self.authenticate_user(email, password)
            
            if auth_result['success']:
                print(f"✅ User {email} authenticated successfully")
                self.log_user_activity(auth_result['user']['id'], 'login')
            else:
                print(f"❌ Authentication failed for {email}")
            
            self.send_json_response(auth_result)
            
        except Exception as e:
            print(f"💥 Sign-in error: {e}")
            self.send_json_response({
                "success": False, 
                "message": "An error occurred during sign-in"
            })
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user credentials"""
        conn = sqlite3.connect('farmconnect.db')
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                SELECT id, full_name, email, farming_experience, farm_type, 
                       location, is_mentor, created_at
                FROM users 
                WHERE email = ? AND password_hash = ?
            ''', (email, password_hash))
            
            user = cursor.fetchone()
            
            if user:
                # Update last login
                cursor.execute(
                    'UPDATE users SET last_login = ? WHERE id = ?',
                    (datetime.now().isoformat(), user[0])
                )
                conn.commit()
                
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
        finally:
            conn.close()
    
    def log_user_activity(self, user_id: int, activity_type: str, details: Dict = None):
        """Log user activity"""
        conn = sqlite3.connect('farmconnect.db')
        cursor = conn.cursor()
        
        try:
            # Create user_activity table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    activity_type TEXT NOT NULL,
                    activity_details TEXT,
                    ip_address TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Get client IP address
            ip_address = self.headers.get('X-Forwarded-For', self.client_address[0])
            
            cursor.execute('''
                INSERT INTO user_activity (user_id, activity_type, activity_details, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (user_id, activity_type, json.dumps(details) if details else None, ip_address))
            
            conn.commit()
        except Exception as e:
            print(f"Warning: Could not log activity: {e}")
        finally:
            conn.close()
    
    def send_json_response(self, data: Dict[str, Any]):
        """Send JSON response with proper headers"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2)
        print(f"📤 Sending response: {response_json}")
        self.wfile.write(response_json.encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_server(port=8000):
    """Run the enhanced signup server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, FarmConnectSignupHandler)
    
    print("🌱 FarmConnect Enhanced Signup Server")
    print("=" * 40)
    print(f"🚀 Server running on port {port}")
    print(f"🌐 Visit http://localhost:{port}")
    print(f"📝 Signup endpoint: http://localhost:{port}/signup")
    print(f"🔐 Signin endpoint: http://localhost:{port}/signin")
    print("=" * 40)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        httpd.server_close()

if __name__ == "__main__":
    # Initialize database first
    import sqlite3
    
    conn = sqlite3.connect('farmconnect.db')
    cursor = conn.cursor()
    
    # Ensure users table exists with all required columns
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
    
    print("✅ Database initialized")
    
    # Start the server
    run_server()
