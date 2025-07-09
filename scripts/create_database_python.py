#!/usr/bin/env python3
"""
FarmConnect PostgreSQL Database Setup Script
Alternative Python method to create database and tables
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys
from pathlib import Path

class DatabaseSetup:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'user': 'postgres',
            'database': 'farmconnect'
        }
        self.admin_config = {
            'host': 'localhost',
            'port': 5432,
            'user': 'postgres',
            'database': 'postgres'  # Connect to default database first
        }
    
    def print_status(self, message, status="info"):
        """Print colored status messages"""
        colors = {
            'info': '\033[0;34m',      # Blue
            'success': '\033[0;32m',   # Green
            'warning': '\033[1;33m',   # Yellow
            'error': '\033[0;31m',     # Red
            'reset': '\033[0m'         # Reset
        }
        
        icons = {
            'info': 'ℹ️ ',
            'success': '✅ ',
            'warning': '⚠️  ',
            'error': '❌ '
        }
        
        color = colors.get(status, colors['info'])
        icon = icons.get(status, '')
        reset = colors['reset']
        
        print(f"{color}{icon}{message}{reset}")
    
    def get_password(self):
        """Get PostgreSQL password from user"""
        import getpass
        
        password = os.environ.get('PGPASSWORD')
        if not password:
            password = getpass.getpass("Enter PostgreSQL password for user 'postgres': ")
        
        return password
    
    def check_postgresql_connection(self, password):
        """Check if we can connect to PostgreSQL"""
        try:
            conn = psycopg2.connect(
                host=self.admin_config['host'],
                port=self.admin_config['port'],
                user=self.admin_config['user'],
                password=password,
                database=self.admin_config['database']
            )
            conn.close()
            self.print_status("PostgreSQL connection successful", "success")
            return True
        except psycopg2.Error as e:
            self.print_status(f"PostgreSQL connection failed: {e}", "error")
            return False
    
    def database_exists(self, password):
        """Check if the farmconnect database exists"""
        try:
            conn = psycopg2.connect(
                host=self.admin_config['host'],
                port=self.admin_config['port'],
                user=self.admin_config['user'],
                password=password,
                database=self.admin_config['database']
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.db_config['database'],)
            )
            
            exists = cursor.fetchone() is not None
            cursor.close()
            conn.close()
            
            return exists
        except psycopg2.Error as e:
            self.print_status(f"Error checking database existence: {e}", "error")
            return False
    
    def create_database(self, password):
        """Create the farmconnect database"""
        try:
            # Check if database already exists
            if self.database_exists(password):
                self.print_status(f"Database '{self.db_config['database']}' already exists", "warning")
                
                response = input("Do you want to drop and recreate it? (y/N): ").strip().lower()
                if response == 'y':
                    self.drop_database(password)
                else:
                    self.print_status("Using existing database", "info")
                    return True
            
            # Create new database
            conn = psycopg2.connect(
                host=self.admin_config['host'],
                port=self.admin_config['port'],
                user=self.admin_config['user'],
                password=password,
                database=self.admin_config['database']
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            cursor.execute(f"CREATE DATABASE {self.db_config['database']}")
            
            cursor.close()
            conn.close()
            
            self.print_status(f"Database '{self.db_config['database']}' created successfully", "success")
            return True
            
        except psycopg2.Error as e:
            self.print_status(f"Error creating database: {e}", "error")
            return False
    
    def drop_database(self, password):
        """Drop the farmconnect database"""
        try:
            conn = psycopg2.connect(
                host=self.admin_config['host'],
                port=self.admin_config['port'],
                user=self.admin_config['user'],
                password=password,
                database=self.admin_config['database']
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Terminate existing connections to the database
            cursor.execute(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '{self.db_config['database']}' AND pid <> pg_backend_pid()
            """)
            
            cursor.execute(f"DROP DATABASE IF EXISTS {self.db_config['database']}")
            
            cursor.close()
            conn.close()
            
            self.print_status(f"Database '{self.db_config['database']}' dropped", "success")
            
        except psycopg2.Error as e:
            self.print_status(f"Error dropping database: {e}", "error")
    
    def run_sql_script(self, password):
        """Run the SQL script to create tables"""
        sql_file = Path(__file__).parent / "farmconnect_postgresql.sql"
        
        if not sql_file.exists():
            self.print_status(f"SQL script '{sql_file}' not found", "error")
            self.print_status("Make sure 'farmconnect_postgresql.sql' is in the same directory", "info")
            return False
        
        try:
            conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=password,
                database=self.db_config['database']
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Read and execute SQL script
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            self.print_status("Executing SQL script...", "info")
            cursor.execute(sql_content)
            
            cursor.close()
            conn.close()
            
            self.print_status("Tables and data created successfully", "success")
            return True
            
        except psycopg2.Error as e:
            self.print_status(f"Error executing SQL script: {e}", "error")
            return False
        except FileNotFoundError:
            self.print_status(f"SQL file not found: {sql_file}", "error")
            return False
    
    def verify_setup(self, password):
        """Verify that the database setup was successful"""
        try:
            conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=password,
                database=self.db_config['database']
            )
            cursor = conn.cursor()
            
            # Check if tables exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = [
                'users', 'posts', 'comments', 'likes', 'mentorships',
                'forum_categories', 'notifications', 'user_activity', 'user_sessions'
            ]
            
            self.print_status("Database verification:", "info")
            for table in expected_tables:
                if table in tables:
                    print(f"  ✅ {table}")
                else:
                    print(f"  ❌ {table} (missing)")
            
            # Get sample data counts
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM posts")
            post_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM forum_categories")
            category_count = cursor.fetchone()[0]
            
            print(f"\nSample data:")
            print(f"  👥 Users: {user_count}")
            print(f"  📝 Posts: {post_count}")
            print(f"  📂 Categories: {category_count}")
            
            cursor.close()
            conn.close()
            
            return True
            
        except psycopg2.Error as e:
            self.print_status(f"Error verifying setup: {e}", "error")
            return False
    
    def show_connection_info(self):
        """Display connection information"""
        print("\n" + "="*50)
        self.print_status("Database setup completed!", "success")
        print("\nConnection Details:")
        print(f"  Host: {self.db_config['host']}")
        print(f"  Port: {self.db_config['port']}")
        print(f"  Database: {self.db_config['database']}")
        print(f"  User: {self.db_config['user']}")
        
        print(f"\nTo connect via command line:")
        print(f"  psql -h {self.db_config['host']} -p {self.db_config['port']} -U {self.db_config['user']} -d {self.db_config['database']}")
        
        print(f"\nSample login credentials (password: password123):")
        print(f"  - john.davis@email.com (Organic Farming Mentor)")
        print(f"  - sarah.martinez@email.com (Beginner Farmer)")
        print(f"  - linda.wilson@email.com (Livestock Expert)")
        print(f"  - michael.johnson@email.com (Organic Certification)")
    
    def setup(self):
        """Main setup process"""
        print("🌱 FarmConnect PostgreSQL Database Setup")
        print("=" * 50)
        
        # Get password
        password = self.get_password()
        
        # Check PostgreSQL connection
        if not self.check_postgresql_connection(password):
            return False
        
        # Create database
        if not self.create_database(password):
            return False
        
        # Run SQL script
        if not self.run_sql_script(password):
            return False
        
        # Verify setup
        if not self.verify_setup(password):
            return False
        
        # Show connection info
        self.show_connection_info()
        
        return True

def main():
    """Main function"""
    setup = DatabaseSetup()
    
    try:
        success = setup.setup()
        if success:
            print("\n🎉 Setup completed successfully!")
        else:
            print("\n💥 Setup failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
