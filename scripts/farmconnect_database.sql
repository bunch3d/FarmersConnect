-- =====================================================
-- FarmConnect Database Schema
-- Complete SQL setup for farming community website
-- =====================================================

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS user_sessions;
DROP TABLE IF EXISTS user_activity;
DROP TABLE IF EXISTS mentorships;
DROP TABLE IF EXISTS likes;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS users;

-- =====================================================
-- USERS TABLE
-- =====================================================
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    farming_experience TEXT NOT NULL CHECK (farming_experience IN ('beginner', 'intermediate', 'experienced')),
    farm_type TEXT NOT NULL CHECK (farm_type IN ('crop', 'livestock', 'mixed', 'organic', 'hydroponics', 'other')),
    location TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP DEFAULT NULL,
    is_mentor BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    profile_image TEXT DEFAULT NULL,
    bio TEXT DEFAULT NULL,
    phone_number TEXT DEFAULT NULL,
    farm_size TEXT DEFAULT NULL,
    years_farming INTEGER DEFAULT NULL
);

-- =====================================================
-- POSTS TABLE
-- =====================================================
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('crops', 'livestock', 'equipment', 'market', 'weather', 'organic', 'general')),
    image_url TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- =====================================================
-- COMMENTS TABLE
-- =====================================================
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    parent_comment_id INTEGER DEFAULT NULL, -- For nested comments
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_edited BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (parent_comment_id) REFERENCES comments (id) ON DELETE CASCADE
);

-- =====================================================
-- LIKES TABLE
-- =====================================================
CREATE TABLE likes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE
);

-- =====================================================
-- MENTORSHIPS TABLE
-- =====================================================
CREATE TABLE mentorships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mentor_id INTEGER NOT NULL,
    mentee_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'declined', 'completed', 'cancelled')),
    message TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accepted_at TIMESTAMP DEFAULT NULL,
    completed_at TIMESTAMP DEFAULT NULL,
    rating INTEGER DEFAULT NULL CHECK (rating >= 1 AND rating <= 5),
    feedback TEXT DEFAULT NULL,
    UNIQUE(mentor_id, mentee_id),
    FOREIGN KEY (mentor_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (mentee_id) REFERENCES users (id) ON DELETE CASCADE
);

-- =====================================================
-- USER ACTIVITY LOG TABLE
-- =====================================================
CREATE TABLE user_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL CHECK (activity_type IN ('login', 'logout', 'post_created', 'comment_added', 'like_given', 'profile_updated')),
    activity_details TEXT DEFAULT NULL,
    ip_address TEXT DEFAULT NULL,
    user_agent TEXT DEFAULT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- =====================================================
-- USER SESSIONS TABLE
-- =====================================================
CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT DEFAULT NULL,
    user_agent TEXT DEFAULT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- =====================================================
-- FORUM CATEGORIES TABLE
-- =====================================================
CREATE TABLE forum_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    icon TEXT DEFAULT NULL,
    color TEXT DEFAULT NULL,
    post_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- NOTIFICATIONS TABLE
-- =====================================================
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('like', 'comment', 'mention', 'mentorship_request', 'mentorship_accepted', 'system')),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    related_id INTEGER DEFAULT NULL, -- ID of related post, comment, etc.
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- User indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_farming_experience ON users(farming_experience);
CREATE INDEX idx_users_is_mentor ON users(is_mentor);
CREATE INDEX idx_users_location ON users(location);

-- Post indexes
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_category ON posts(category);
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);
CREATE INDEX idx_posts_likes_count ON posts(likes_count DESC);

-- Comment indexes
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_comments_created_at ON comments(created_at);

-- Like indexes
CREATE INDEX idx_likes_user_id ON likes(user_id);
CREATE INDEX idx_likes_post_id ON likes(post_id);

-- Mentorship indexes
CREATE INDEX idx_mentorships_mentor_id ON mentorships(mentor_id);
CREATE INDEX idx_mentorships_mentee_id ON mentorships(mentee_id);
CREATE INDEX idx_mentorships_status ON mentorships(status);

-- Activity indexes
CREATE INDEX idx_user_activity_user_id ON user_activity(user_id);
CREATE INDEX idx_user_activity_timestamp ON user_activity(timestamp DESC);

-- Session indexes
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);

-- =====================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- =====================================================

-- Update post updated_at timestamp when post is modified
CREATE TRIGGER update_post_timestamp 
    AFTER UPDATE ON posts
    FOR EACH ROW
BEGIN
    UPDATE posts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update comment updated_at timestamp when comment is modified
CREATE TRIGGER update_comment_timestamp 
    AFTER UPDATE ON comments
    FOR EACH ROW
BEGIN
    UPDATE comments SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Automatically increment post likes_count when a like is added
CREATE TRIGGER increment_post_likes 
    AFTER INSERT ON likes
    FOR EACH ROW
BEGIN
    UPDATE posts SET likes_count = likes_count + 1 WHERE id = NEW.post_id;
END;

-- Automatically decrement post likes_count when a like is removed
CREATE TRIGGER decrement_post_likes 
    AFTER DELETE ON likes
    FOR EACH ROW
BEGIN
    UPDATE posts SET likes_count = likes_count - 1 WHERE id = OLD.post_id;
END;

-- Automatically increment post comments_count when a comment is added
CREATE TRIGGER increment_post_comments 
    AFTER INSERT ON comments
    FOR EACH ROW
BEGIN
    UPDATE posts SET comments_count = comments_count + 1 WHERE id = NEW.post_id;
END;

-- Automatically decrement post comments_count when a comment is deleted
CREATE TRIGGER decrement_post_comments 
    AFTER DELETE ON comments
    FOR EACH ROW
BEGIN
    UPDATE posts SET comments_count = comments_count - 1 WHERE id = OLD.post_id;
END;

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- View for posts with user information
CREATE VIEW posts_with_users AS
SELECT 
    p.id,
    p.title,
    p.content,
    p.category,
    p.image_url,
    p.created_at,
    p.updated_at,
    p.likes_count,
    p.comments_count,
    p.is_pinned,
    u.id as user_id,
    u.full_name as author_name,
    u.farming_experience as author_experience,
    u.is_mentor as author_is_mentor,
    u.location as author_location
FROM posts p
JOIN users u ON p.user_id = u.id
WHERE p.is_archived = FALSE
ORDER BY p.is_pinned DESC, p.created_at DESC;

-- View for mentorship statistics
CREATE VIEW mentorship_stats AS
SELECT 
    u.id,
    u.full_name,
    u.farming_experience,
    u.farm_type,
    u.location,
    COUNT(CASE WHEN m.status = 'accepted' THEN 1 END) as active_mentorships,
    COUNT(CASE WHEN m.status = 'completed' THEN 1 END) as completed_mentorships,
    AVG(CASE WHEN m.rating IS NOT NULL THEN m.rating END) as average_rating
FROM users u
LEFT JOIN mentorships m ON u.id = m.mentor_id
WHERE u.is_mentor = TRUE
GROUP BY u.id, u.full_name, u.farming_experience, u.farm_type, u.location;

-- =====================================================
-- SAMPLE DATA INSERTION
-- =====================================================

-- Insert forum categories
INSERT INTO forum_categories (name, description, icon, color) VALUES
('Crops & Planting', 'Discuss seed varieties, planting techniques, and crop management', 'fas fa-seedling', '#4a7c59'),
('Livestock', 'Share experiences about animal husbandry and livestock care', 'fas fa-cow', '#8b4513'),
('Equipment & Tools', 'Reviews and recommendations for farming equipment', 'fas fa-tools', '#2d5016'),
('Market & Pricing', 'Market trends, pricing strategies, and selling tips', 'fas fa-chart-line', '#daa520'),
('Weather & Climate', 'Weather patterns and climate impact on farming', 'fas fa-cloud-sun', '#87ceeb'),
('Organic Farming', 'Sustainable and organic farming practices', 'fas fa-leaf', '#228b22'),
('General Discussion', 'General farming topics and community chat', 'fas fa-comments', '#6b7280');

-- Insert sample users (passwords are hashed version of 'password123')
INSERT INTO users (full_name, email, password_hash, farming_experience, farm_type, location, is_mentor, bio, years_farming, farm_size) VALUES
('John Davis', 'john.davis@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'experienced', 'organic', 'Iowa, USA', TRUE, 'Organic farming specialist with 25 years of experience. Passionate about sustainable agriculture and mentoring new farmers.', 25, '500 acres'),
('Sarah Martinez', 'sarah.martinez@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'beginner', 'crop', 'California, USA', FALSE, 'New to farming and excited to learn from the community. Recently purchased my first 50-acre plot.', 1, '50 acres'),
('Robert Brown', 'robert.brown@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'experienced', 'mixed', 'Texas, USA', TRUE, 'Third-generation farmer specializing in mixed crop and livestock operations.', 30, '1200 acres'),
('Linda Wilson', 'linda.wilson@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'experienced', 'livestock', 'Texas, USA', TRUE, 'Cattle ranching expert with focus on sustainable grazing practices and animal welfare.', 18, '800 acres'),
('Michael Johnson', 'michael.johnson@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'experienced', 'organic', 'Iowa, USA', TRUE, 'Pioneer in organic certification processes and sustainable farming techniques.', 22, '300 acres'),
('Anna Garcia', 'anna.garcia@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'experienced', 'hydroponics', 'Florida, USA', TRUE, 'Hydroponic farming specialist and controlled environment agriculture expert.', 15, '10 acres'),
('David Lee', 'david.lee@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'experienced', 'crop', 'California, USA', TRUE, 'Technology integration specialist focusing on precision agriculture and data analytics.', 20, '2000 acres'),
('Emma Thompson', 'emma.thompson@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'intermediate', 'organic', 'Oregon, USA', FALSE, 'Transitioning to organic farming and learning sustainable practices.', 5, '150 acres'),
('Carlos Rodriguez', 'carlos.rodriguez@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'beginner', 'crop', 'Arizona, USA', FALSE, 'Urban farming enthusiast starting my first commercial operation.', 2, '25 acres'),
('Jennifer Kim', 'jennifer.kim@email.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'intermediate', 'mixed', 'Wisconsin, USA', FALSE, 'Family farm operation focusing on dairy and crop rotation.', 8, '400 acres');

-- Insert sample posts
INSERT INTO posts (user_id, title, content, category, created_at) VALUES
(1, 'Best practices for organic pest control?', 'I''ve been transitioning to organic farming and looking for effective, natural pest control methods. What has worked best for you? I''m particularly dealing with aphids on my tomato plants. Any recommendations for companion planting or natural sprays?', 'organic', datetime('now', '-2 hours')),
(2, 'First-time farmer seeking advice on soil preparation', 'Hi everyone! I just bought my first piece of land and I''m excited to start farming. The soil test results show low nitrogen levels. What''s the best way to improve soil fertility naturally? Should I focus on cover crops or composting first?', 'crops', datetime('now', '-5 hours')),
(3, 'Weather patterns affecting crop yields this season', 'Has anyone else noticed unusual weather patterns this growing season? My corn yields are down 15% compared to last year. Wondering if it''s just my area or a broader trend. How are you adapting your planting schedules?', 'weather', datetime('now', '-1 day')),
(4, 'Sustainable grazing rotation strategies', 'Looking to optimize our pasture management. Currently rotating cattle every 2 weeks but wondering if shorter intervals might be better for grass recovery. What rotation schedules work best for your operations?', 'livestock', datetime('now', '-2 days')),
(5, 'Organic certification process - tips and timeline', 'For those considering organic certification, here''s what I learned from my experience. The process took 18 months and required detailed record-keeping. Happy to share my documentation templates if anyone is interested.', 'organic', datetime('now', '-3 days')),
(6, 'Hydroponic lettuce production optimization', 'Sharing my latest results from LED lighting experiments in hydroponic lettuce production. Managed to increase yields by 23% while reducing energy costs. Details on nutrient solutions and lighting schedules in the comments.', 'crops', datetime('now', '-4 days')),
(7, 'Precision agriculture ROI analysis', 'After 3 years of implementing precision agriculture technologies, here''s my honest assessment of costs vs benefits. GPS guidance and variable rate application have been game-changers, but some technologies didn''t pay off as expected.', 'equipment', datetime('now', '-5 days')),
(8, 'Transitioning to no-till farming', 'Made the switch to no-till last season and seeing promising results. Soil health is improving and fuel costs are down 30%. However, weed management has been challenging. What cover crop mixes work best for weed suppression?', 'crops', datetime('now', '-6 days')),
(9, 'Urban farming challenges and solutions', 'Starting my urban farming operation has been quite the learning experience. Space limitations and zoning regulations are the biggest hurdles. Anyone else dealing with similar challenges in urban agriculture?', 'general', datetime('now', '-1 week')),
(10, 'Dairy farming automation benefits', 'Recently installed automated milking systems and the results have been impressive. Milk quality is up, labor costs down, and cow health monitoring is much more precise. Happy to discuss the investment and implementation process.', 'livestock', datetime('now', '-1 week'));

-- Insert sample comments
INSERT INTO comments (post_id, user_id, content, created_at) VALUES
(1, 4, 'For aphids, I''ve had great success with ladybug releases and neem oil spray. Also, planting marigolds nearby helps deter them naturally.', datetime('now', '-1 hour')),
(1, 6, 'Companion planting with basil and nasturtiums works well too. The strong scents confuse the aphids and other pests.', datetime('now', '-45 minutes')),
(2, 1, 'Start with a soil test to understand exactly what nutrients you''re missing. Cover crops like crimson clover can fix nitrogen naturally.', datetime('now', '-4 hours')),
(2, 5, 'Composting is excellent for long-term soil health. I''d recommend starting both cover crops and composting simultaneously.', datetime('now', '-3 hours')),
(3, 7, 'We''re seeing similar patterns in California. I''ve started using weather prediction models to adjust planting dates by 2-3 weeks.', datetime('now', '-20 hours')),
(4, 3, 'We do 7-day rotations and it''s been working well. The key is monitoring grass height - move when it''s grazed to 3-4 inches.', datetime('now', '-1 day')),
(5, 2, 'This is so helpful! I''m just starting the certification process. Would love to see those documentation templates.', datetime('now', '-2 days')),
(6, 8, 'Impressive results! What LED spectrum are you using? I''m considering upgrading my greenhouse lighting system.', datetime('now', '-3 days'));

-- Insert sample likes
INSERT INTO likes (user_id, post_id) VALUES
(2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1), -- Post 1: 9 likes
(1, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2), -- Post 2: 8 likes
(1, 3), (2, 3), (4, 3), (5, 3), (6, 3), (7, 3), -- Post 3: 6 likes
(1, 4), (2, 4), (3, 4), (5, 4), (6, 4), -- Post 4: 5 likes
(1, 5), (2, 5), (3, 5), (4, 5), -- Post 5: 4 likes
(1, 6), (2, 6), (3, 6), -- Post 6: 3 likes
(1, 7), (2, 7), -- Post 7: 2 likes
(1, 8); -- Post 8: 1 like

-- Insert sample mentorships
INSERT INTO mentorships (mentor_id, mentee_id, status, message, accepted_at) VALUES
(1, 2, 'accepted', 'I''d love to help you get started with organic farming practices.', datetime('now', '-1 week')),
(4, 9, 'accepted', 'Happy to share my experience with livestock management.', datetime('now', '-5 days')),
(5, 8, 'pending', 'Interested in learning about your organic certification process.', NULL),
(6, 2, 'pending', 'Would like guidance on hydroponic systems for my operation.', NULL),
(7, 10, 'accepted', 'Let''s discuss precision agriculture implementation for your dairy farm.', datetime('now', '-3 days'));

-- Insert sample notifications
INSERT INTO notifications (user_id, type, title, message, related_id) VALUES
(2, 'mentorship_accepted', 'Mentorship Request Accepted', 'John Davis has accepted your mentorship request!', 1),
(1, 'comment', 'New Comment on Your Post', 'Linda Wilson commented on your post about organic pest control.', 1),
(2, 'like', 'Post Liked', 'Your post received a new like from Michael Johnson.', 2),
(9, 'mentorship_accepted', 'Mentorship Request Accepted', 'Linda Wilson has accepted your mentorship request!', 2);

-- =====================================================
-- STORED PROCEDURES (Functions in SQLite)
-- =====================================================

-- Note: SQLite doesn't support stored procedures, but we can create views for complex queries

-- View for user dashboard statistics
CREATE VIEW user_dashboard_stats AS
SELECT 
    u.id,
    u.full_name,
    COUNT(DISTINCT p.id) as total_posts,
    COUNT(DISTINCT c.id) as total_comments,
    SUM(p.likes_count) as total_likes_received,
    COUNT(DISTINCT CASE WHEN m.mentor_id = u.id AND m.status = 'accepted' THEN m.id END) as active_mentorships_as_mentor,
    COUNT(DISTINCT CASE WHEN m.mentee_id = u.id AND m.status = 'accepted' THEN m.id END) as active_mentorships_as_mentee
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
LEFT JOIN comments c ON u.id = c.user_id
LEFT JOIN mentorships m ON u.id = m.mentor_id OR u.id = m.mentee_id
GROUP BY u.id, u.full_name;

-- View for trending posts (most liked in last 7 days)
CREATE VIEW trending_posts AS
SELECT 
    p.*,
    u.full_name as author_name,
    u.farming_experience as author_experience
FROM posts p
JOIN users u ON p.user_id = u.id
WHERE p.created_at >= datetime('now', '-7 days')
ORDER BY p.likes_count DESC, p.comments_count DESC
LIMIT 10;

-- =====================================================
-- FINAL STATISTICS QUERY
-- =====================================================

-- Display database statistics
SELECT 'Database Setup Complete!' as status;
SELECT 'Total Users: ' || COUNT(*) as user_count FROM users;
SELECT 'Total Posts: ' || COUNT(*) as post_count FROM posts;
SELECT 'Total Comments: ' || COUNT(*) as comment_count FROM comments;
SELECT 'Total Likes: ' || COUNT(*) as like_count FROM likes;
SELECT 'Total Mentorships: ' || COUNT(*) as mentorship_count FROM mentorships;

-- =====================================================
-- LOGIN CREDENTIALS FOR TESTING
-- =====================================================

/*
SAMPLE LOGIN CREDENTIALS (Password: password123 for all):

🌱 MENTORS:
- john.davis@email.com (Organic Farming Expert)
- robert.brown@email.com (Mixed Farming Specialist)  
- linda.wilson@email.com (Livestock Expert)
- michael.johnson@email.com (Organic Certification)
- anna.garcia@email.com (Hydroponics Specialist)
- david.lee@email.com (Precision Agriculture)

👨‍🌾 FARMERS:
- sarah.martinez@email.com (Beginner)
- emma.thompson@email.com (Intermediate)
- carlos.rodriguez@email.com (Beginner - Urban)
- jennifer.kim@email.com (Intermediate - Dairy)
*/
