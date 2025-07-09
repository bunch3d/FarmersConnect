-- =====================================================
-- FarmConnect Database Schema - PostgreSQL Version
-- Complete PostgreSQL setup for farming community website
-- =====================================================

-- Create database (run this separately as superuser)
-- CREATE DATABASE farmconnect;
-- \c farmconnect;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom types/enums
CREATE TYPE farming_experience_type AS ENUM ('beginner', 'intermediate', 'experienced');
CREATE TYPE farm_type_enum AS ENUM ('crop', 'livestock', 'mixed', 'organic', 'hydroponics', 'other');
CREATE TYPE post_category_enum AS ENUM ('crops', 'livestock', 'equipment', 'market', 'weather', 'organic', 'general');
CREATE TYPE mentorship_status_enum AS ENUM ('pending', 'accepted', 'declined', 'completed', 'cancelled');
CREATE TYPE activity_type_enum AS ENUM ('login', 'logout', 'post_created', 'comment_added', 'like_given', 'profile_updated');
CREATE TYPE notification_type_enum AS ENUM ('like', 'comment', 'mention', 'mentorship_request', 'mentorship_accepted', 'system');

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS user_sessions CASCADE;
DROP TABLE IF EXISTS user_activity CASCADE;
DROP TABLE IF EXISTS mentorships CASCADE;
DROP TABLE IF EXISTS likes CASCADE;
DROP TABLE IF EXISTS comments CASCADE;
DROP TABLE IF EXISTS posts CASCADE;
DROP TABLE IF EXISTS forum_categories CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- =====================================================
-- USERS TABLE
-- =====================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    farming_experience farming_experience_type NOT NULL,
    farm_type farm_type_enum NOT NULL,
    location VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    is_mentor BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    profile_image TEXT,
    bio TEXT,
    phone_number VARCHAR(20),
    farm_size VARCHAR(50),
    years_farming INTEGER CHECK (years_farming >= 0),
    website_url VARCHAR(255),
    social_media JSONB DEFAULT '{}',
    preferences JSONB DEFAULT '{}',
    email_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP WITH TIME ZONE
);

-- =====================================================
-- FORUM CATEGORIES TABLE
-- =====================================================
CREATE TABLE forum_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    icon VARCHAR(50),
    color VARCHAR(7), -- Hex color code
    post_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- POSTS TABLE
-- =====================================================
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id UUID REFERENCES forum_categories(id),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    content_html TEXT, -- Rendered HTML version
    image_urls TEXT[], -- Array of image URLs
    tags VARCHAR(50)[], -- Array of tags
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    views_count INTEGER DEFAULT 0,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    search_vector tsvector, -- Full-text search
    location_data JSONB, -- Geographic data
    metadata JSONB DEFAULT '{}'
);

-- =====================================================
-- COMMENTS TABLE
-- =====================================================
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    parent_comment_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    content_html TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_edited BOOLEAN DEFAULT FALSE,
    edit_history JSONB DEFAULT '[]',
    likes_count INTEGER DEFAULT 0,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- =====================================================
-- LIKES TABLE
-- =====================================================
CREATE TABLE likes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    comment_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT likes_target_check CHECK (
        (post_id IS NOT NULL AND comment_id IS NULL) OR 
        (post_id IS NULL AND comment_id IS NOT NULL)
    ),
    UNIQUE(user_id, post_id),
    UNIQUE(user_id, comment_id)
);

-- =====================================================
-- MENTORSHIPS TABLE
-- =====================================================
CREATE TABLE mentorships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mentor_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mentee_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status mentorship_status_enum DEFAULT 'pending',
    message TEXT,
    mentor_response TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    accepted_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback TEXT,
    goals TEXT[],
    progress_notes JSONB DEFAULT '[]',
    meeting_schedule JSONB,
    UNIQUE(mentor_id, mentee_id)
);

-- =====================================================
-- USER ACTIVITY LOG TABLE
-- =====================================================
CREATE TABLE user_activity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    activity_type activity_type_enum NOT NULL,
    activity_details JSONB,
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- =====================================================
-- USER SESSIONS TABLE
-- =====================================================
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    device_info JSONB,
    is_active BOOLEAN DEFAULT TRUE
);

-- =====================================================
-- NOTIFICATIONS TABLE
-- =====================================================
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type notification_type_enum NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    related_id UUID, -- Generic reference to related entity
    related_type VARCHAR(50), -- Type of related entity (post, comment, etc.)
    data JSONB DEFAULT '{}',
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- User indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_farming_experience ON users(farming_experience);
CREATE INDEX idx_users_is_mentor ON users(is_mentor);
CREATE INDEX idx_users_location ON users USING gin(to_tsvector('english', location));
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_last_login ON users(last_login);

-- Post indexes
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_category_id ON posts(category_id);
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);
CREATE INDEX idx_posts_likes_count ON posts(likes_count DESC);
CREATE INDEX idx_posts_views_count ON posts(views_count DESC);
CREATE INDEX idx_posts_is_pinned ON posts(is_pinned, created_at DESC);
CREATE INDEX idx_posts_tags ON posts USING gin(tags);
CREATE INDEX idx_posts_search ON posts USING gin(search_vector);
CREATE INDEX idx_posts_location ON posts USING gin(location_data);

-- Comment indexes
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_comments_parent_id ON comments(parent_comment_id);
CREATE INDEX idx_comments_created_at ON comments(created_at);

-- Like indexes
CREATE INDEX idx_likes_user_id ON likes(user_id);
CREATE INDEX idx_likes_post_id ON likes(post_id);
CREATE INDEX idx_likes_comment_id ON likes(comment_id);
CREATE INDEX idx_likes_created_at ON likes(created_at);

-- Mentorship indexes
CREATE INDEX idx_mentorships_mentor_id ON mentorships(mentor_id);
CREATE INDEX idx_mentorships_mentee_id ON mentorships(mentee_id);
CREATE INDEX idx_mentorships_status ON mentorships(status);
CREATE INDEX idx_mentorships_created_at ON mentorships(created_at);

-- Activity indexes
CREATE INDEX idx_user_activity_user_id ON user_activity(user_id);
CREATE INDEX idx_user_activity_timestamp ON user_activity(timestamp DESC);
CREATE INDEX idx_user_activity_type ON user_activity(activity_type);
CREATE INDEX idx_user_activity_ip ON user_activity(ip_address);

-- Session indexes
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX idx_user_sessions_active ON user_sessions(is_active, expires_at);

-- Notification indexes
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX idx_notifications_type ON notifications(type);

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to update search vector for posts
CREATE OR REPLACE FUNCTION update_post_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('english', 
        COALESCE(NEW.title, '') || ' ' || 
        COALESCE(NEW.content, '') || ' ' ||
        COALESCE(array_to_string(NEW.tags, ' '), '')
    );
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to increment/decrement counters
CREATE OR REPLACE FUNCTION update_post_counters()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF TG_TABLE_NAME = 'likes' AND NEW.post_id IS NOT NULL THEN
            UPDATE posts SET likes_count = likes_count + 1 WHERE id = NEW.post_id;
        ELSIF TG_TABLE_NAME = 'comments' THEN
            UPDATE posts SET comments_count = comments_count + 1 WHERE id = NEW.post_id;
        END IF;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        IF TG_TABLE_NAME = 'likes' AND OLD.post_id IS NOT NULL THEN
            UPDATE posts SET likes_count = likes_count - 1 WHERE id = OLD.post_id;
        ELSIF TG_TABLE_NAME = 'comments' THEN
            UPDATE posts SET comments_count = comments_count - 1 WHERE id = OLD.post_id;
        END IF;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Function to update category post count
CREATE OR REPLACE FUNCTION update_category_post_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE forum_categories SET post_count = post_count + 1 WHERE id = NEW.category_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE forum_categories SET post_count = post_count - 1 WHERE id = OLD.category_id;
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' AND OLD.category_id != NEW.category_id THEN
        UPDATE forum_categories SET post_count = post_count - 1 WHERE id = OLD.category_id;
        UPDATE forum_categories SET post_count = post_count + 1 WHERE id = NEW.category_id;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Create triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_posts_updated_at BEFORE UPDATE ON posts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_comments_updated_at BEFORE UPDATE ON comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON forum_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_post_search_vector_trigger BEFORE INSERT OR UPDATE ON posts
    FOR EACH ROW EXECUTE FUNCTION update_post_search_vector();

CREATE TRIGGER update_post_likes_count AFTER INSERT OR DELETE ON likes
    FOR EACH ROW EXECUTE FUNCTION update_post_counters();

CREATE TRIGGER update_post_comments_count AFTER INSERT OR DELETE ON comments
    FOR EACH ROW EXECUTE FUNCTION update_post_counters();

CREATE TRIGGER update_category_count AFTER INSERT OR UPDATE OR DELETE ON posts
    FOR EACH ROW EXECUTE FUNCTION update_category_post_count();

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- View for posts with user information and category
CREATE VIEW posts_with_details AS
SELECT 
    p.id,
    p.title,
    p.content,
    p.image_urls,
    p.tags,
    p.created_at,
    p.updated_at,
    p.likes_count,
    p.comments_count,
    p.views_count,
    p.is_pinned,
    p.is_featured,
    u.id as user_id,
    u.full_name as author_name,
    u.farming_experience as author_experience,
    u.is_mentor as author_is_mentor,
    u.location as author_location,
    u.profile_image as author_avatar,
    fc.name as category_name,
    fc.color as category_color,
    fc.icon as category_icon
FROM posts p
JOIN users u ON p.user_id = u.id
LEFT JOIN forum_categories fc ON p.category_id = fc.id
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
    u.bio,
    COUNT(CASE WHEN m.status = 'accepted' THEN 1 END) as active_mentorships,
    COUNT(CASE WHEN m.status = 'completed' THEN 1 END) as completed_mentorships,
    ROUND(AVG(CASE WHEN m.rating IS NOT NULL THEN m.rating END), 2) as average_rating,
    COUNT(m.rating) as total_ratings
FROM users u
LEFT JOIN mentorships m ON u.id = m.mentor_id
WHERE u.is_mentor = TRUE AND u.is_active = TRUE
GROUP BY u.id, u.full_name, u.farming_experience, u.farm_type, u.location, u.bio;

-- View for user dashboard statistics
CREATE VIEW user_dashboard_stats AS
SELECT 
    u.id,
    u.full_name,
    u.email,
    u.farming_experience,
    u.farm_type,
    u.location,
    u.created_at,
    u.last_login,
    COUNT(DISTINCT p.id) as total_posts,
    COUNT(DISTINCT c.id) as total_comments,
    COALESCE(SUM(p.likes_count), 0) as total_likes_received,
    COUNT(DISTINCT CASE WHEN m.mentor_id = u.id AND m.status = 'accepted' THEN m.id END) as active_mentorships_as_mentor,
    COUNT(DISTINCT CASE WHEN m.mentee_id = u.id AND m.status = 'accepted' THEN m.id END) as active_mentorships_as_mentee,
    COUNT(DISTINCT n.id) FILTER (WHERE n.is_read = FALSE) as unread_notifications
FROM users u
LEFT JOIN posts p ON u.id = p.user_id AND p.is_archived = FALSE
LEFT JOIN comments c ON u.id = c.user_id AND c.is_deleted = FALSE
LEFT JOIN mentorships m ON u.id = m.mentor_id OR u.id = m.mentee_id
LEFT JOIN notifications n ON u.id = n.user_id
GROUP BY u.id, u.full_name, u.email, u.farming_experience, u.farm_type, u.location, u.created_at, u.last_login;

-- View for trending posts (most engagement in last 7 days)
CREATE VIEW trending_posts AS
SELECT 
    p.*,
    u.full_name as author_name,
    u.farming_experience as author_experience,
    fc.name as category_name,
    (p.likes_count * 2 + p.comments_count * 3 + p.views_count * 0.1) as engagement_score
FROM posts p
JOIN users u ON p.user_id = u.id
LEFT JOIN forum_categories fc ON p.category_id = fc.id
WHERE p.created_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
    AND p.is_archived = FALSE
ORDER BY engagement_score DESC, p.created_at DESC
LIMIT 20;

-- =====================================================
-- STORED PROCEDURES
-- =====================================================

-- Function to get user activity summary
CREATE OR REPLACE FUNCTION get_user_activity_summary(user_uuid UUID, days_back INTEGER DEFAULT 30)
RETURNS TABLE(
    activity_date DATE,
    login_count BIGINT,
    post_count BIGINT,
    comment_count BIGINT,
    like_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ua.timestamp::DATE as activity_date,
        COUNT(*) FILTER (WHERE ua.activity_type = 'login') as login_count,
        COUNT(*) FILTER (WHERE ua.activity_type = 'post_created') as post_count,
        COUNT(*) FILTER (WHERE ua.activity_type = 'comment_added') as comment_count,
        COUNT(*) FILTER (WHERE ua.activity_type = 'like_given') as like_count
    FROM user_activity ua
    WHERE ua.user_id = user_uuid 
        AND ua.timestamp >= CURRENT_TIMESTAMP - (days_back || ' days')::INTERVAL
    GROUP BY ua.timestamp::DATE
    ORDER BY activity_date DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to search posts with full-text search
CREATE OR REPLACE FUNCTION search_posts(
    search_query TEXT,
    category_filter UUID DEFAULT NULL,
    limit_count INTEGER DEFAULT 20,
    offset_count INTEGER DEFAULT 0
)
RETURNS TABLE(
    id UUID,
    title VARCHAR,
    content TEXT,
    author_name VARCHAR,
    category_name VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE,
    likes_count INTEGER,
    comments_count INTEGER,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.title,
        p.content,
        u.full_name as author_name,
        fc.name as category_name,
        p.created_at,
        p.likes_count,
        p.comments_count,
        ts_rank(p.search_vector, plainto_tsquery('english', search_query)) as rank
    FROM posts p
    JOIN users u ON p.user_id = u.id
    LEFT JOIN forum_categories fc ON p.category_id = fc.id
    WHERE p.search_vector @@ plainto_tsquery('english', search_query)
        AND p.is_archived = FALSE
        AND (category_filter IS NULL OR p.category_id = category_filter)
    ORDER BY rank DESC, p.created_at DESC
    LIMIT limit_count OFFSET offset_count;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- SAMPLE DATA INSERTION
-- =====================================================

-- Insert forum categories
INSERT INTO forum_categories (name, description, icon, color, sort_order) VALUES
('Crops & Planting', 'Discuss seed varieties, planting techniques, and crop management', 'fas fa-seedling', '#4a7c59', 1),
('Livestock', 'Share experiences about animal husbandry and livestock care', 'fas fa-cow', '#8b4513', 2),
('Equipment & Tools', 'Reviews and recommendations for farming equipment', 'fas fa-tools', '#2d5016', 3),
('Market & Pricing', 'Market trends, pricing strategies, and selling tips', 'fas fa-chart-line', '#daa520', 4),
('Weather & Climate', 'Weather patterns and climate impact on farming', 'fas fa-cloud-sun', '#87ceeb', 5),
('Organic Farming', 'Sustainable and organic farming practices', 'fas fa-leaf', '#228b22', 6),
('General Discussion', 'General farming topics and community chat', 'fas fa-comments', '#6b7280', 7);

-- Insert sample users (using crypt for password hashing)
INSERT INTO users (full_name, email, password_hash, farming_experience, farm_type, location, is_mentor, bio, years_farming, farm_size, social_media, preferences) VALUES
('John Davis', 'john.davis@email.com', crypt('password123', gen_salt('bf')), 'experienced', 'organic', 'Iowa, USA', TRUE, 'Organic farming specialist with 25 years of experience. Passionate about sustainable agriculture and mentoring new farmers.', 25, '500 acres', '{"twitter": "@johndavis_farm", "instagram": "johndavis_organic"}', '{"email_notifications": true, "theme": "light"}'),
('Sarah Martinez', 'sarah.martinez@email.com', crypt('password123', gen_salt('bf')), 'beginner', 'crop', 'California, USA', FALSE, 'New to farming and excited to learn from the community. Recently purchased my first 50-acre plot.', 1, '50 acres', '{"instagram": "sarahs_farm_journey"}', '{"email_notifications": true, "theme": "light"}'),
('Robert Brown', 'robert.brown@email.com', crypt('password123', gen_salt('bf')), 'experienced', 'mixed', 'Texas, USA', TRUE, 'Third-generation farmer specializing in mixed crop and livestock operations.', 30, '1200 acres', '{"facebook": "BrownFamilyFarm"}', '{"email_notifications": false, "theme": "dark"}'),
('Linda Wilson', 'linda.wilson@email.com', crypt('password123', gen_salt('bf')), 'experienced', 'livestock', 'Texas, USA', TRUE, 'Cattle ranching expert with focus on sustainable grazing practices and animal welfare.', 18, '800 acres', '{"youtube": "WilsonRanch"}', '{"email_notifications": true, "theme": "light"}'),
('Michael Johnson', 'michael.johnson@email.com', crypt('password123', gen_salt('bf')), 'experienced', 'organic', 'Iowa, USA', TRUE, 'Pioneer in organic certification processes and sustainable farming techniques.', 22, '300 acres', '{"twitter": "@organic_mike"}', '{"email_notifications": true, "theme": "light"}'),
('Anna Garcia', 'anna.garcia@email.com', crypt('password123', gen_salt('bf')), 'experienced', 'hydroponics', 'Florida, USA', TRUE, 'Hydroponic farming specialist and controlled environment agriculture expert.', 15, '10 acres', '{"instagram": "hydro_anna", "youtube": "AnnaHydroponics"}', '{"email_notifications": true, "theme": "light"}'),
('David Lee', 'david.lee@email.com', crypt('password123', gen_salt('bf')), 'experienced', 'crop', 'California, USA', TRUE, 'Technology integration specialist focusing on precision agriculture and data analytics.', 20, '2000 acres', '{"linkedin": "david-lee-agtech"}', '{"email_notifications": false, "theme": "dark"}'),
('Emma Thompson', 'emma.thompson@email.com', crypt('password123', gen_salt('bf')), 'intermediate', 'organic', 'Oregon, USA', FALSE, 'Transitioning to organic farming and learning sustainable practices.', 5, '150 acres', '{}', '{"email_notifications": true, "theme": "light"}'),
('Carlos Rodriguez', 'carlos.rodriguez@email.com', crypt('password123', gen_salt('bf')), 'beginner', 'crop', 'Arizona, USA', FALSE, 'Urban farming enthusiast starting my first commercial operation.', 2, '25 acres', '{"instagram": "carlos_urban_farm"}', '{"email_notifications": true, "theme": "light"}'),
('Jennifer Kim', 'jennifer.kim@email.com', crypt('password123', gen_salt('bf')), 'intermediate', 'mixed', 'Wisconsin, USA', FALSE, 'Family farm operation focusing on dairy and crop rotation.', 8, '400 acres', '{"facebook": "KimFamilyDairy"}', '{"email_notifications": true, "theme": "light"}');

-- Get category IDs for posts
DO $$
DECLARE
    crops_cat_id UUID;
    livestock_cat_id UUID;
    organic_cat_id UUID;
    weather_cat_id UUID;
    equipment_cat_id UUID;
    general_cat_id UUID;
    user_john UUID;
    user_sarah UUID;
    user_robert UUID;
    user_linda UUID;
    user_michael UUID;
    user_anna UUID;
    user_david UUID;
    user_emma UUID;
    user_carlos UUID;
    user_jennifer UUID;
BEGIN
    -- Get category IDs
    SELECT id INTO crops_cat_id FROM forum_categories WHERE name = 'Crops & Planting';
    SELECT id INTO livestock_cat_id FROM forum_categories WHERE name = 'Livestock';
    SELECT id INTO organic_cat_id FROM forum_categories WHERE name = 'Organic Farming';
    SELECT id INTO weather_cat_id FROM forum_categories WHERE name = 'Weather & Climate';
    SELECT id INTO equipment_cat_id FROM forum_categories WHERE name = 'Equipment & Tools';
    SELECT id INTO general_cat_id FROM forum_categories WHERE name = 'General Discussion';
    
    -- Get user IDs
    SELECT id INTO user_john FROM users WHERE email = 'john.davis@email.com';
    SELECT id INTO user_sarah FROM users WHERE email = 'sarah.martinez@email.com';
    SELECT id INTO user_robert FROM users WHERE email = 'robert.brown@email.com';
    SELECT id INTO user_linda FROM users WHERE email = 'linda.wilson@email.com';
    SELECT id INTO user_michael FROM users WHERE email = 'michael.johnson@email.com';
    SELECT id INTO user_anna FROM users WHERE email = 'anna.garcia@email.com';
    SELECT id INTO user_david FROM users WHERE email = 'david.lee@email.com';
    SELECT id INTO user_emma FROM users WHERE email = 'emma.thompson@email.com';
    SELECT id INTO user_carlos FROM users WHERE email = 'carlos.rodriguez@email.com';
    SELECT id INTO user_jennifer FROM users WHERE email = 'jennifer.kim@email.com';

    -- Insert sample posts
    INSERT INTO posts (user_id, category_id, title, content, tags, created_at) VALUES
    (user_john, organic_cat_id, 'Best practices for organic pest control?', 'I''ve been transitioning to organic farming and looking for effective, natural pest control methods. What has worked best for you? I''m particularly dealing with aphids on my tomato plants. Any recommendations for companion planting or natural sprays?', ARRAY['organic', 'pest-control', 'tomatoes', 'aphids'], CURRENT_TIMESTAMP - INTERVAL '2 hours'),
    (user_sarah, crops_cat_id, 'First-time farmer seeking advice on soil preparation', 'Hi everyone! I just bought my first piece of land and I''m excited to start farming. The soil test results show low nitrogen levels. What''s the best way to improve soil fertility naturally? Should I focus on cover crops or composting first?', ARRAY['beginner', 'soil', 'nitrogen', 'cover-crops'], CURRENT_TIMESTAMP - INTERVAL '5 hours'),
    (user_robert, weather_cat_id, 'Weather patterns affecting crop yields this season', 'Has anyone else noticed unusual weather patterns this growing season? My corn yields are down 15% compared to last year. Wondering if it''s just my area or a broader trend. How are you adapting your planting schedules?', ARRAY['weather', 'corn', 'yields', 'climate'], CURRENT_TIMESTAMP - INTERVAL '1 day'),
    (user_linda, livestock_cat_id, 'Sustainable grazing rotation strategies', 'Looking to optimize our pasture management. Currently rotating cattle every 2 weeks but wondering if shorter intervals might be better for grass recovery. What rotation schedules work best for your operations?', ARRAY['livestock', 'grazing', 'cattle', 'pasture'], CURRENT_TIMESTAMP - INTERVAL '2 days'),
    (user_michael, organic_cat_id, 'Organic certification process - tips and timeline', 'For those considering organic certification, here''s what I learned from my experience. The process took 18 months and required detailed record-keeping. Happy to share my documentation templates if anyone is interested.', ARRAY['organic', 'certification', 'documentation'], CURRENT_TIMESTAMP - INTERVAL '3 days'),
    (user_anna, crops_cat_id, 'Hydroponic lettuce production optimization', 'Sharing my latest results from LED lighting experiments in hydroponic lettuce production. Managed to increase yields by 23% while reducing energy costs. Details on nutrient solutions and lighting schedules in the comments.', ARRAY['hydroponics', 'lettuce', 'led', 'yields'], CURRENT_TIMESTAMP - INTERVAL '4 days'),
    (user_david, equipment_cat_id, 'Precision agriculture ROI analysis', 'After 3 years of implementing precision agriculture technologies, here''s my honest assessment of costs vs benefits. GPS guidance and variable rate application have been game-changers, but some technologies didn''t pay off as expected.', ARRAY['precision-agriculture', 'roi', 'gps', 'technology'], CURRENT_TIMESTAMP - INTERVAL '5 days'),
    (user_emma, crops_cat_id, 'Transitioning to no-till farming', 'Made the switch to no-till last season and seeing promising results. Soil health is improving and fuel costs are down 30%. However, weed management has been challenging. What cover crop mixes work best for weed suppression?', ARRAY['no-till', 'soil-health', 'cover-crops', 'weeds'], CURRENT_TIMESTAMP - INTERVAL '6 days'),
    (user_carlos, general_cat_id, 'Urban farming challenges and solutions', 'Starting my urban farming operation has been quite the learning experience. Space limitations and zoning regulations are the biggest hurdles. Anyone else dealing with similar challenges in urban agriculture?', ARRAY['urban-farming', 'zoning', 'space', 'challenges'], CURRENT_TIMESTAMP - INTERVAL '1 week'),
    (user_jennifer, livestock_cat_id, 'Dairy farming automation benefits', 'Recently installed automated milking systems and the results have been impressive. Milk quality is up, labor costs down, and cow health monitoring is much more precise. Happy to discuss the investment and implementation process.', ARRAY['dairy', 'automation', 'milking', 'technology'], CURRENT_TIMESTAMP - INTERVAL '1 week');
END $$;

-- =====================================================
-- FINAL SETUP AND STATISTICS
-- =====================================================

-- Create a function to display database statistics
CREATE OR REPLACE FUNCTION get_database_stats()
RETURNS TABLE(
    stat_name TEXT,
    stat_value BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'Total Users'::TEXT, COUNT(*)::BIGINT FROM users
    UNION ALL
    SELECT 'Total Posts'::TEXT, COUNT(*)::BIGINT FROM posts
    UNION ALL
    SELECT 'Total Comments'::TEXT, COUNT(*)::BIGINT FROM comments
    UNION ALL
    SELECT 'Total Likes'::TEXT, COUNT(*)::BIGINT FROM likes
    UNION ALL
    SELECT 'Total Mentorships'::TEXT, COUNT(*)::BIGINT FROM mentorships
    UNION ALL
    SELECT 'Active Mentors'::TEXT, COUNT(*)::BIGINT FROM users WHERE is_mentor = TRUE
    UNION ALL
    SELECT 'Forum Categories'::TEXT, COUNT(*)::BIGINT FROM forum_categories;
END;
$$ LANGUAGE plpgsql;

-- Display setup completion message and statistics
SELECT 'FarmConnect PostgreSQL Database Setup Complete!' as status;
SELECT * FROM get_database_stats();

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

🔧 ADVANCED FEATURES:
- Full-text search on posts
- UUID primary keys for better scalability
- JSONB columns for flexible data storage
- Proper password hashing with bcrypt
- Comprehensive indexing for performance
- Stored procedures for complex queries
- Triggers for automatic updates
- Views for common data access patterns
*/
