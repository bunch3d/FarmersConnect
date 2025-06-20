import sqlite3
from datetime import datetime

class MentorshipManager:
    def __init__(self, db_path='farmconnect.db'):
        self.db_path = db_path
    
    def request_mentorship(self, mentee_id, mentor_id):
        """Request mentorship from a mentor"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if request already exists
            cursor.execute('''
                SELECT id FROM mentorships 
                WHERE mentor_id = ? AND mentee_id = ?
            ''', (mentor_id, mentee_id))
            
            existing_request = cursor.fetchone()
            
            if existing_request:
                conn.close()
                return {"success": False, "message": "Mentorship request already exists!"}
            
            cursor.execute('''
                INSERT INTO mentorships (mentor_id, mentee_id, status)
                VALUES (?, ?, 'pending')
            ''', (mentor_id, mentee_id))
            
            conn.commit()
            request_id = cursor.lastrowid
            conn.close()
            
            return {"success": True, "request_id": request_id, "message": "Mentorship request sent successfully!"}
            
        except Exception as e:
            conn.close()
            return {"success": False, "message": f"Error sending request: {str(e)}"}
    
    def get_available_mentors(self, specialty=None):
        """Get list of available mentors"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if specialty:
            cursor.execute('''
                SELECT id, full_name, farming_experience, farm_type, location
                FROM users 
                WHERE is_mentor = 1 AND farm_type = ?
                ORDER BY full_name
            ''', (specialty,))
        else:
            cursor.execute('''
                SELECT id, full_name, farming_experience, farm_type, location
                FROM users 
                WHERE is_mentor = 1
                ORDER BY full_name
            ''')
        
        mentors = cursor.fetchall()
        conn.close()
        
        mentor_list = []
        for mentor in mentors:
            mentor_list.append({
                "id": mentor[0],
                "full_name": mentor[1],
                "farming_experience": mentor[2],
                "specialty": mentor[3],
                "location": mentor[4]
            })
        
        return {"success": True, "mentors": mentor_list}
    
    def accept_mentorship(self, mentor_id, mentee_id):
        """Accept a mentorship request"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE mentorships 
                SET status = 'accepted'
                WHERE mentor_id = ? AND mentee_id = ? AND status = 'pending'
            ''', (mentor_id, mentee_id))
            
            if cursor.rowcount == 0:
                conn.close()
                return {"success": False, "message": "No pending request found!"}
            
            conn.commit()
            conn.close()
            
            return {"success": True, "message": "Mentorship request accepted!"}
            
        except Exception as e:
            conn.close()
            return {"success": False, "message": f"Error accepting request: {str(e)}"}
    
    def get_mentorship_requests(self, mentor_id):
        """Get pending mentorship requests for a mentor"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.id, m.created_at, u.full_name, u.farming_experience, u.farm_type, u.location
            FROM mentorships m
            JOIN users u ON m.mentee_id = u.id
            WHERE m.mentor_id = ? AND m.status = 'pending'
            ORDER BY m.created_at DESC
        ''', (mentor_id,))
        
        requests = cursor.fetchall()
        conn.close()
        
        request_list = []
        for request in requests:
            request_list.append({
                "id": request[0],
                "created_at": request[1],
                "mentee_name": request[2],
                "mentee_experience": request[3],
                "mentee_farm_type": request[4],
                "mentee_location": request[5]
            })
        
        return {"success": True, "requests": request_list}

# Example usage
if __name__ == "__main__":
    mentorship_manager = MentorshipManager()
    
    # Test getting available mentors
    mentors = mentorship_manager.get_available_mentors()
    print("Available mentors:", mentors)
    
    # Test requesting mentorship
    result = mentorship_manager.request_mentorship(2, 1)  # mentee_id=2, mentor_id=1
    print("Mentorship request result:", result)
