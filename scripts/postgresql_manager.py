import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
import uuid
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Any

class PostgreSQLFarmConnectManager:
    def __init__(self, 
                 host: str = "localhost", 
                 database: str = "farmconnect", 
                 user: str = "postgres", 
                 password: str = "password",
                 port: int = 5432):
        """Initialize PostgreSQL connection"""
        self.connection_params = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
            'port': port
        }
        self.conn = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.conn.autocommit = True
            print("✅ Connected to PostgreSQL database successfully!")
        except psycopg2.Error as e:
            print(f"❌ Error connecting to PostgreSQL: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("🔒 Database connection closed")
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute a query and return results"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if cursor.description:
                    return [dict(row) for row in cursor.fetchall()]
                return []
        except psycopg2.Error as e:
            print(f"❌ Database error: {e}")
            raise
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_user(self, full_name: str, email: str, password: str, 
                   farming_experience: str, farm_type: str, location: str,
                   is_mentor: bool = False, bio: str = None) -> Dict:
        """Create a new user account"""
        try:
            user_id = str(uuid.uuid4())
            password_hash = self.hash_password(password)
            
            query = """
                INSERT INTO users (id, full_name, email, password_hash, farming_experience, 
                                 farm_type, location, is_mentor, bio)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, full_name, email, created_at
            """
            
            result = self.execute_query(query, (
                user_id, full_name, email, password_hash, farming_experience,
                farm_type, location, is_mentor, bio
            ))
            
            if result:
                print(f"✅ User {full_name} created successfully!")
                return {"success": True, "user": result[0]}
            
        except psycopg2.IntegrityError:
            return {"success": False, "message": "Email already exists!"}
        except Exception as e:
            return {"success": False, "message": f"Error creating user: {str(e)}"}
    
    def authenticate_user(self, email: str, password: str) -> Dict:
        """Authenticate user login"""
        try:
            query = """
                SELECT id, full_name, email, password_hash, farming_experience, 
                       farm_type, location, is_mentor, bio, created_at
                FROM users 
                WHERE email = %s AND is_active = TRUE
            """
            
            result = self.execute_query(query, (email,))
            
            if result and self.verify_password(password, result[0]['password_hash']):
                user_data = result[0]
                del user_data['password_hash']  # Remove password hash from response
                
                # Update last login
                self.execute_query(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
                    (user_data['id'],)
                )
                
                # Log login activity
                self.log_user_activity(user_data['id'], 'login')
                
                print(f"✅ User {email} authenticated successfully!")
                return {"success": True, "user": user_data}
            else:
                return {"success": False, "message": "Invalid email or password"}
                
        except Exception as e:
            return {"success": False, "message": f"Authentication error: {str(e)}"}
    
    def create_post(self, user_id: str, title: str, content: str, 
                   category_name: str, tags: List[str] = None) -> Dict:
        """Create a new forum post"""
        try:
            # Get category ID
            category_query = "SELECT id FROM forum_categories WHERE name = %s"
            category_result = self.execute_query(category_query, (category_name,))
            
            if not category_result:
                return {"success": False, "message": "Invalid category"}
            
            category_id = category_result[0]['id']
            post_id = str(uuid.uuid4())
            
            query = """
                INSERT INTO posts (id, user_id, category_id, title, content, tags)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, title, created_at
            """
            
            result = self.execute_query(query, (
                post_id, user_id, category_id, title, content, tags or []
            ))
            
            if result:
                # Log activity
                self.log_user_activity(user_id, 'post_created', {'post_id': post_id})
                print(f"✅ Post '{title}' created successfully!")
                return {"success": True, "post": result[0]}
                
        except Exception as e:
            return {"success": False, "message": f"Error creating post: {str(e)}"}
    
    def get_posts(self, category_name: str = None, limit: int = 20, offset: int = 0) -> Dict:
        """Get forum posts with optional category filter"""
        try:
            if category_name:
                query = """
                    SELECT p.id, p.title, p.content, p.tags, p.created_at, p.likes_count, 
                           p.comments_count, p.views_count, u.full_name as author_name,
                           u.farming_experience as author_experience, fc.name as category_name
                    FROM posts p
                    JOIN users u ON p.user_id = u.id
                    JOIN forum_categories fc ON p.category_id = fc.id
                    WHERE fc.name = %s AND p.is_archived = FALSE
                    ORDER BY p.is_pinned DESC, p.created_at DESC
                    LIMIT %s OFFSET %s
                """
                params = (category_name, limit, offset)
            else:
                query = """
                    SELECT p.id, p.title, p.content, p.tags, p.created_at, p.likes_count, 
                           p.comments_count, p.views_count, u.full_name as author_name,
                           u.farming_experience as author_experience, fc.name as category_name
                    FROM posts p
                    JOIN users u ON p.user_id = u.id
                    LEFT JOIN forum_categories fc ON p.category_id = fc.id
                    WHERE p.is_archived = FALSE
                    ORDER BY p.is_pinned DESC, p.created_at DESC
                    LIMIT %s OFFSET %s
                """
                params = (limit, offset)
            
            posts = self.execute_query(query, params)
            return {"success": True, "posts": posts}
            
        except Exception as e:
            return {"success": False, "message": f"Error fetching posts: {str(e)}"}
    
    def search_posts(self, search_query: str, limit: int = 20) -> Dict:
        """Search posts using full-text search"""
        try:
            query = "SELECT * FROM search_posts(%s, NULL, %s, 0)"
            results = self.execute_query(query, (search_query, limit))
            return {"success": True, "posts": results}
        except Exception as e:
            return {"success": False, "message": f"Search error: {str(e)}"}
    
    def like_post(self, user_id: str, post_id: str) -> Dict:
        """Like or unlike a post"""
        try:
            # Check if already liked
            check_query = "SELECT id FROM likes WHERE user_id = %s AND post_id = %s"
            existing = self.execute_query(check_query, (user_id, post_id))
            
            if existing:
                # Unlike
                self.execute_query("DELETE FROM likes WHERE user_id = %s AND post_id = %s", 
                                 (user_id, post_id))
                action = "unliked"
            else:
                # Like
                like_id = str(uuid.uuid4())
                self.execute_query("INSERT INTO likes (id, user_id, post_id) VALUES (%s, %s, %s)",
                                 (like_id, user_id, post_id))
                action = "liked"
                
                # Log activity
                self.log_user_activity(user_id, 'like_given', {'post_id': post_id})
            
            return {"success": True, "action": action}
            
        except Exception as e:
            return {"success": False, "message": f"Error processing like: {str(e)}"}
    
    def add_comment(self, user_id: str, post_id: str, content: str, 
                   parent_comment_id: str = None) -> Dict:
        """Add a comment to a post"""
        try:
            comment_id = str(uuid.uuid4())
            
            query = """
                INSERT INTO comments (id, post_id, user_id, content, parent_comment_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, content, created_at
            """
            
            result = self.execute_query(query, (
                comment_id, post_id, user_id, content, parent_comment_id
            ))
            
            if result:
                # Log activity
                self.log_user_activity(user_id, 'comment_added', {
                    'post_id': post_id, 
                    'comment_id': comment_id
                })
                return {"success": True, "comment": result[0]}
                
        except Exception as e:
            return {"success": False, "message": f"Error adding comment: {str(e)}"}
    
    def get_available_mentors(self, specialty: str = None) -> Dict:
        """Get list of available mentors"""
        try:
            if specialty:
                query = """
                    SELECT * FROM mentorship_stats 
                    WHERE farm_type = %s
                    ORDER BY average_rating DESC NULLS LAST, completed_mentorships DESC
                """
                params = (specialty,)
            else:
                query = """
                    SELECT * FROM mentorship_stats 
                    ORDER BY average_rating DESC NULLS LAST, completed_mentorships DESC
                """
                params = ()
            
            mentors = self.execute_query(query, params)
            return {"success": True, "mentors": mentors}
            
        except Exception as e:
            return {"success": False, "message": f"Error fetching mentors: {str(e)}"}
    
    def request_mentorship(self, mentee_id: str, mentor_id: str, message: str = None) -> Dict:
        """Request mentorship from a mentor"""
        try:
            mentorship_id = str(uuid.uuid4())
            
            query = """
                INSERT INTO mentorships (id, mentor_id, mentee_id, message)
                VALUES (%s, %s, %s, %s)
                RETURNING id, created_at
            """
            
            result = self.execute_query(query, (mentorship_id, mentor_id, mentee_id, message))
            
            if result:
                # Create notification for mentor
                self.create_notification(
                    mentor_id, 
                    'mentorship_request',
                    'New Mentorship Request',
                    f'You have received a new mentorship request.',
                    mentorship_id
                )
                
                return {"success": True, "mentorship": result[0]}
                
        except psycopg2.IntegrityError:
            return {"success": False, "message": "Mentorship request already exists"}
        except Exception as e:
            return {"success": False, "message": f"Error requesting mentorship: {str(e)}"}
    
    def create_notification(self, user_id: str, notification_type: str, 
                          title: str, message: str, related_id: str = None) -> Dict:
        """Create a notification for a user"""
        try:
            notification_id = str(uuid.uuid4())
            
            query = """
                INSERT INTO notifications (id, user_id, type, title, message, related_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, created_at
            """
            
            result = self.execute_query(query, (
                notification_id, user_id, notification_type, title, message, related_id
            ))
            
            return {"success": True, "notification": result[0]} if result else {"success": False}
            
        except Exception as e:
            return {"success": False, "message": f"Error creating notification: {str(e)}"}
    
    def log_user_activity(self, user_id: str, activity_type: str, 
                         details: Dict = None, ip_address: str = None) -> None:
        """Log user activity"""
        try:
            activity_id = str(uuid.uuid4())
            
            query = """
                INSERT INTO user_activity (id, user_id, activity_type, activity_details, ip_address)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            self.execute_query(query, (
                activity_id, user_id, activity_type, 
                json.dumps(details) if details else None, ip_address
            ))
            
        except Exception as e:
            print(f"Warning: Could not log activity: {e}")
    
    def get_user_dashboard_stats(self, user_id: str) -> Dict:
        """Get dashboard statistics for a user"""
        try:
            query = "SELECT * FROM user_dashboard_stats WHERE id = %s"
            result = self.execute_query(query, (user_id,))
            
            if result:
                return {"success": True, "stats": result[0]}
            else:
                return {"success": False, "message": "User not found"}
                
        except Exception as e:
            return {"success": False, "message": f"Error fetching stats: {str(e)}"}
    
    def get_trending_posts(self) -> Dict:
        """Get trending posts"""
        try:
            query = "SELECT * FROM trending_posts"
            posts = self.execute_query(query)
            return {"success": True, "posts": posts}
        except Exception as e:
            return {"success": False, "message": f"Error fetching trending posts: {str(e)}"}

# Example usage and testing
if __name__ == "__main__":
    # Initialize database manager
    db = PostgreSQLFarmConnectManager()
    
    try:
        print("🧪 Testing PostgreSQL FarmConnect Database...")
        print("=" * 50)
        
        # Test authentication
        print("\n🔐 Testing Authentication:")
        auth_result = db.authenticate_user("john.davis@email.com", "password123")
        if auth_result['success']:
            user = auth_result['user']
            print(f"✅ Authenticated: {user['full_name']} ({user['farming_experience']})")
            
            # Test dashboard stats
            print(f"\n📊 Dashboard Stats for {user['full_name']}:")
            stats = db.get_user_dashboard_stats(user['id'])
            if stats['success']:
                user_stats = stats['stats']
                print(f"Posts: {user_stats['total_posts']}")
                print(f"Comments: {user_stats['total_comments']}")
                print(f"Likes Received: {user_stats['total_likes_received']}")
                print(f"Active Mentorships: {user_stats['active_mentorships_as_mentor']}")
        
        # Test post search
        print(f"\n🔍 Testing Full-Text Search:")
        search_results = db.search_posts("organic farming")
        if search_results['success']:
            print(f"Found {len(search_results['posts'])} posts matching 'organic farming'")
            for post in search_results['posts'][:3]:
                print(f"- {post['title']} (Rank: {post['rank']:.3f})")
        
        # Test trending posts
        print(f"\n📈 Trending Posts:")
        trending = db.get_trending_posts()
        if trending['success']:
            for post in trending['posts'][:5]:
                print(f"- {post['title']} (Score: {post['engagement_score']:.1f})")
        
        # Test mentors
        print(f"\n👨‍🌾 Available Mentors:")
        mentors = db.get_available_mentors()
        if mentors['success']:
            for mentor in mentors['mentors'][:3]:
                rating = mentor['average_rating'] or 0
                print(f"- {mentor['full_name']} ({mentor['farm_type']}) - Rating: {rating:.1f}")
        
        print(f"\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        db.disconnect()
