import sqlite3
from datetime import datetime

class ForumManager:
    def __init__(self, db_path='farmconnect.db'):
        self.db_path = db_path
    
    def create_post(self, user_id, title, content, category):
        """Create a new forum post"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO posts (user_id, title, content, category)
                VALUES (?, ?, ?, ?)
            ''', (user_id, title, content, category))
            
            conn.commit()
            post_id = cursor.lastrowid
            conn.close()
            
            print(f"Post created successfully with ID: {post_id}")
            return {"success": True, "post_id": post_id, "message": "Post created successfully!"}
            
        except Exception as e:
            conn.close()
            return {"success": False, "message": f"Error creating post: {str(e)}"}
    
    def get_posts(self, category=None, limit=20, offset=0):
        """Get forum posts with optional category filter"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT p.id, p.title, p.content, p.category, p.created_at, p.likes_count, p.comments_count,
                       u.full_name, u.farming_experience
                FROM posts p
                JOIN users u ON p.user_id = u.id
                WHERE p.category = ?
                ORDER BY p.created_at DESC
                LIMIT ? OFFSET ?
            ''', (category, limit, offset))
        else:
            cursor.execute('''
                SELECT p.id, p.title, p.content, p.category, p.created_at, p.likes_count, p.comments_count,
                       u.full_name, u.farming_experience
                FROM posts p
                JOIN users u ON p.user_id = u.id
                ORDER BY p.created_at DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))
        
        posts = cursor.fetchall()
        conn.close()
        
        post_list = []
        for post in posts:
            post_list.append({
                "id": post[0],
                "title": post[1],
                "content": post[2],
                "category": post[3],
                "created_at": post[4],
                "likes_count": post[5],
                "comments_count": post[6],
                "author_name": post[7],
                "author_experience": post[8]
            })
        
        return {"success": True, "posts": post_list}
    
    def like_post(self, user_id, post_id):
        """Like or unlike a post"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if user already liked this post
        cursor.execute('''
            SELECT id FROM likes WHERE user_id = ? AND post_id = ?
        ''', (user_id, post_id))
        
        existing_like = cursor.fetchone()
        
        if existing_like:
            # Unlike the post
            cursor.execute('''
                DELETE FROM likes WHERE user_id = ? AND post_id = ?
            ''', (user_id, post_id))
            
            cursor.execute('''
                UPDATE posts SET likes_count = likes_count - 1 WHERE id = ?
            ''', (post_id,))
            
            action = "unliked"
        else:
            # Like the post
            cursor.execute('''
                INSERT INTO likes (user_id, post_id) VALUES (?, ?)
            ''', (user_id, post_id))
            
            cursor.execute('''
                UPDATE posts SET likes_count = likes_count + 1 WHERE id = ?
            ''', (post_id,))
            
            action = "liked"
        
        conn.commit()
        conn.close()
        
        return {"success": True, "action": action}
    
    def add_comment(self, user_id, post_id, content):
        """Add a comment to a post"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO comments (post_id, user_id, content)
                VALUES (?, ?, ?)
            ''', (post_id, user_id, content))
            
            # Update comment count
            cursor.execute('''
                UPDATE posts SET comments_count = comments_count + 1 WHERE id = ?
            ''', (post_id,))
            
            conn.commit()
            comment_id = cursor.lastrowid
            conn.close()
            
            return {"success": True, "comment_id": comment_id, "message": "Comment added successfully!"}
            
        except Exception as e:
            conn.close()
            return {"success": False, "message": f"Error adding comment: {str(e)}"}
    
    def get_comments(self, post_id):
        """Get comments for a specific post"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.id, c.content, c.created_at, u.full_name, u.farming_experience
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.post_id = ?
            ORDER BY c.created_at ASC
        ''', (post_id,))
        
        comments = cursor.fetchall()
        conn.close()
        
        comment_list = []
        for comment in comments:
            comment_list.append({
                "id": comment[0],
                "content": comment[1],
                "created_at": comment[2],
                "author_name": comment[3],
                "author_experience": comment[4]
            })
        
        return {"success": True, "comments": comment_list}

# Example usage
if __name__ == "__main__":
    forum_manager = ForumManager()
    
    # Test creating a post
    result = forum_manager.create_post(
        1,
        "Test Post Title",
        "This is a test post content about farming techniques.",
        "crops"
    )
    print("Create post result:", result)
    
    # Test getting posts
    posts = forum_manager.get_posts()
    print("Posts:", posts)
