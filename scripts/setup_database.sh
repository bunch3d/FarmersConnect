#!/bin/bash

# =====================================================
# FarmConnect PostgreSQL Database Setup Script
# Run this script to create the database and tables
# =====================================================

echo "🌱 FarmConnect PostgreSQL Database Setup"
echo "========================================"

# Database configuration
DB_NAME="farmconnect"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if PostgreSQL is installed and running
check_postgresql() {
    print_info "Checking PostgreSQL installation..."
    
    if ! command -v psql &> /dev/null; then
        print_error "PostgreSQL is not installed or not in PATH"
        echo "Please install PostgreSQL first:"
        echo "  - Windows: Download from https://www.postgresql.org/download/windows/"
        echo "  - macOS: brew install postgresql"
        echo "  - Ubuntu: sudo apt-get install postgresql postgresql-contrib"
        exit 1
    fi
    
    print_status "PostgreSQL is installed"
}

# Create database if it doesn't exist
create_database() {
    print_info "Creating database '$DB_NAME'..."
    
    # Check if database exists
    DB_EXISTS=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; echo $?)
    
    if [ $DB_EXISTS -eq 0 ]; then
        print_warning "Database '$DB_NAME' already exists"
        read -p "Do you want to drop and recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Dropping existing database..."
            dropdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME
            print_status "Database dropped"
        else
            print_info "Using existing database"
            return 0
        fi
    fi
    
    # Create new database
    createdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME
    if [ $? -eq 0 ]; then
        print_status "Database '$DB_NAME' created successfully"
    else
        print_error "Failed to create database '$DB_NAME'"
        exit 1
    fi
}

# Run SQL script
run_sql_script() {
    print_info "Running SQL script to create tables..."
    
    if [ ! -f "farmconnect_postgresql.sql" ]; then
        print_error "SQL script 'farmconnect_postgresql.sql' not found"
        print_info "Make sure you're running this script from the scripts directory"
        exit 1
    fi
    
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f farmconnect_postgresql.sql
    
    if [ $? -eq 0 ]; then
        print_status "Tables created successfully"
    else
        print_error "Failed to create tables"
        exit 1
    fi
}

# Display connection info
show_connection_info() {
    echo
    print_status "Database setup completed!"
    echo
    print_info "Connection Details:"
    echo "  Host: $DB_HOST"
    echo "  Port: $DB_PORT"
    echo "  Database: $DB_NAME"
    echo "  User: $DB_USER"
    echo
    print_info "To connect to the database:"
    echo "  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
    echo
    print_info "Sample login credentials (password: password123):"
    echo "  - john.davis@email.com (Mentor)"
    echo "  - sarah.martinez@email.com (Beginner)"
    echo "  - linda.wilson@email.com (Livestock Expert)"
}

# Main execution
main() {
    check_postgresql
    create_database
    run_sql_script
    show_connection_info
}

# Run main function
main
