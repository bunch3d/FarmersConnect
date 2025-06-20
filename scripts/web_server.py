from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from user_management import UserManager
from forum_management import ForumManager
from mentorship_management import MentorshipManager

class FarmConnectHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.user_manager = UserManager()
        self.forum_manager = ForumManager()
        self.mentorship_manager = MentorshipManager()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/api/posts':
            self.handle_get_posts()
        elif self.path.startswith('/api/mentors'):
            self.handle_get_mentors()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/signup':
            self.handle_signup()
        elif self.path == '/signin':
            self.handle_signin()
        elif self.path == '/api/posts':
            self.handle_create_post()
        elif self.path == '/api/like':
            self.handle_like_post()
        elif self.path == '/api/comment':
            self.handle_add_comment()
        elif self.path == '/api/mentorship/request':
            self.handle_mentorship_request()
        else:
            self.send_error(404, "Not Found")
    
    def handle_signup(self):
        """Handle user signup"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            # Parse form data
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            full_name = form_data.get('fullName', [''])[0]
            email = form_data.get('email', [''])[0]
            password = form_data.get('password', [''])[0]
            farming_experience = form_data.get('farmingExperience', [''])[0]
            farm_type = form_data.get('farmType', [''])[0]
            location = form_data.get('location', [''])[0]
            
            result = self.user_manager.create_user(
                full_name, email, password, farming_experience, farm_type, location
            )
            
            self.send_json_response(result)
            
        except Exception as e:
            self.send_json_response({"success": False, "message": f"Server error: {str(e)}"})
    
    def handle_signin(self):
        """Handle user signin"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            email = form_data.get('email', [''])[0]
            password = form_data.get('password', [''])[0]
            
            result = self.user_manager.authenticate_user(email, password)
            
            self.send_json_response(result)
            
        except Exception as e:
            self.send_json_response({"success": False, "message": f"Server error: {str(e)}"})
    
    def handle_get_posts(self):
        """Handle getting forum posts"""
        try:
            posts = self.forum_manager.get_posts()
            self.send_json_response(posts)
        except Exception as e:
            self.send_json_response({"success": False, "message": f"Server error: {str(e)}"})
    
    def handle_create_post(self):
        """Handle creating a new post"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            result = self.forum_manager.create_post(
                data['user_id'],
                data['title'],
                data['content'],
                data['category']
            )
            
            self.send_json_response(result)
            
        except Exception as e:
            self.send_json_response({"success": False, "message": f"Server error: {str(e)}"})
    
    def handle_like_post(self):
        """Handle liking a post"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            result = self.forum_manager.like_post(
                data['user_id'],
                data['post_id']
            )
            
            self.send_json_response(result)
            
        except Exception as e:
            self.send_json_response({"success": False, "message": f"Server error: {str(e)}"})
    
    def handle_get_mentors(self):
        """Handle getting available mentors"""
        try:
            mentors = self.mentorship_manager.get_available_mentors()
            self.send_json_response(mentors)
        except Exception as e:
            self.send_json_response({"success": False, "message": f"Server error: {str(e)}"})
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

def run_server(port=8000):
    """Run the web server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, FarmConnectHandler)
    print(f"FarmConnect server running on port {port}")
    print(f"Visit http://localhost:{port} to access the website")
    httpd.serve_forever()

if __name__ == "__main__":
    # Initialize database first
    from database_setup import create_database, seed_sample_data
    create_database()
    seed_sample_data()
    
    # Start the server
    run_server()
