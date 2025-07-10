#!/usr/bin/env python3
"""
Simple Test Server for FarmConnect
This is a minimal server to test basic connectivity
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from datetime import datetime

class SimpleTestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        print(f"GET request to: {self.path}")
        
        if self.path == '/':
            self.send_html_response("""
            <html>
            <head><title>FarmConnect Test Server</title></head>
            <body>
                <h1>🌱 FarmConnect Test Server is Running!</h1>
                <p>Server is working correctly.</p>
                <p>Time: {}</p>
                <ul>
                    <li><a href="/debug/db-info">Database Info</a></li>
                    <li><a href="/debug/test">Test Endpoint</a></li>
                </ul>
            </body>
            </html>
            """.format(datetime.now().isoformat()))
        
        elif self.path == '/debug/db-info':
            self.send_json_response({
                "success": True,
                "message": "Database info endpoint working",
                "timestamp": datetime.now().isoformat(),
                "server": "Simple Test Server"
            })
        
        elif self.path == '/debug/test':
            self.send_json_response({
                "success": True,
                "message": "Test endpoint working",
                "timestamp": datetime.now().isoformat()
            })
        
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        print(f"POST request to: {self.path}")
        
        # Read POST data
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            # Try to parse as form data
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            print(f"Form data received: {form_data}")
        except:
            print(f"Raw POST data: {post_data}")
        
        if self.path == '/signup':
            self.send_json_response({
                "success": True,
                "message": "Signup endpoint working (test mode)",
                "received_data": str(form_data) if 'form_data' in locals() else "Could not parse data",
                "timestamp": datetime.now().isoformat()
            })
        
        elif self.path == '/signin':
            self.send_json_response({
                "success": True,
                "message": "Signin endpoint working (test mode)",
                "received_data": str(form_data) if 'form_data' in locals() else "Could not parse data",
                "timestamp": datetime.now().isoformat()
            })
        
        elif self.path == '/debug/test-db':
            self.send_json_response({
                "success": True,
                "message": "Database test endpoint working",
                "timestamp": datetime.now().isoformat()
            })
        
        else:
            self.send_error(404, "Not Found")
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        print(f"OPTIONS request to: {self.path}")
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def send_json_response(self, data):
        """Send JSON response with CORS headers"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2)
        print(f"Sending JSON response: {response_json}")
        self.wfile.write(response_json.encode('utf-8'))
    
    def send_html_response(self, html):
        """Send HTML response"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to add timestamps"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {format % args}")

def run_simple_server(port=8000):
    """Run the simple test server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleTestHandler)
    
    print("🧪 FarmConnect Simple Test Server")
    print("=" * 40)
    print(f"🚀 Server running on port {port}")
    print(f"🌐 Visit: http://localhost:{port}")
    print(f"🔍 Test endpoints:")
    print(f"   - GET  /                - Home page")
    print(f"   - GET  /debug/db-info   - Database info")
    print(f"   - GET  /debug/test      - Test endpoint")
    print(f"   - POST /signup          - Signup test")
    print(f"   - POST /signin          - Signin test")
    print("=" * 40)
    print("This is a minimal server for testing connectivity.")
    print("It will respond to requests but won't create real users.")
    print("=" * 40)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        httpd.server_close()

if __name__ == "__main__":
    run_simple_server()
