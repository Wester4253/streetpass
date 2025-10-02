#!/bin/bash

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}StreetPass Setup Script${NC}"
echo "------------------------"

# Function to check last command status
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1${NC}"
        exit 1
    fi
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

echo "Installing system dependencies..."
apt-get update
apt-get install -y python3.11 \
                   python3.11-venv \
                   python3-pip \
                   imagemagick \
                   libsqlite3-dev
check_status "System dependencies installed"

# Create directories if they don't exist
echo "Setting up directories..."
mkdir -p backend/app/static/icons
mkdir -p backend/avatars
mkdir -p backend/tests
check_status "Directories created"

# Create Python virtual environment
echo "Setting up Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate
check_status "Virtual environment created"

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt
check_status "Python dependencies installed"

# Generate app icons
echo "Generating default icons..."
convert app/static/icons/icon-512x512.svg app/static/icons/icon-512x512.png
convert app/static/icons/icon-192x192.svg app/static/icons/icon-192x192.png
convert app/static/icons/icon-192x192.svg -resize 128x128 app/static/icons/default.png
check_status "Icons generated"

# Setup environment
echo "Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    # Generate a random secret key
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/changeme-supersecret/$SECRET_KEY/" .env
    check_status "Environment file created with secure secret key"
else
    echo -e "${BLUE}Using existing .env file${NC}"
fi

# Initialize database
echo "Initializing database..."
python3 -c "from app.db.session import init_db; init_db()"
check_status "Database initialized"

# Start the server
echo "Starting server..."
./start-prod.sh &
SERVER_PID=$!

# Wait for server to start
sleep 3
if ps -p $SERVER_PID > /dev/null; then
    echo -e "${GREEN}Server started successfully!${NC}"
    echo -e "${BLUE}Server Status:${NC}"
    echo "- PID: $SERVER_PID"
    echo "- URL: http://localhost:8000"
    echo "- Database: $(pwd)/streetpass.db"
    echo "- Avatars: $(pwd)/avatars"
    echo -e "\n${BLUE}Monitoring server logs:${NC}"
    tail -f nohup.out
else
    echo -e "${RED}Server failed to start${NC}"
    exit 1
fi
