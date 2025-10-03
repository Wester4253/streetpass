#!/bin/bash

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Error handling
set -e
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
trap 'echo -e "${RED}\"${last_command}\" command failed with exit code $?.${NC}"' EXIT

# Function to check if a port is in use
check_port() {
    nc -z localhost $1 >/dev/null 2>&1
}

# Function to wait for a service to be ready
wait_for_service() {
    local port=$1
    local service=$2
    local count=0
    echo -ne "${YELLOW}Waiting for $service to start"
    while ! nc -z localhost $port; do
        if [ $count -gt 30 ]; then
            echo -e "${RED}\n$service failed to start within 30 seconds${NC}"
            exit 1
        fi
        echo -n "."
        sleep 1
        ((count++))
    done
    echo -e "${GREEN}OK${NC}"
}

echo -e "${BLUE}StreetPass Development Setup${NC}"
echo "-------------------------"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is required but not installed.${NC}"
    exit 1
fi

# Create and activate virtual environment
echo -e "\n${BLUE}Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo -e "\n${BLUE}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r backend/requirements.txt

# Create necessary directories
echo -e "\n${BLUE}Creating necessary directories...${NC}"
mkdir -p backend/avatars
mkdir -p backend/app/static/icons

# Generate app icons
echo -e "\n${BLUE}Generating app icons...${NC}"
if command -v convert &> /dev/null; then
    convert frontend/icons/icon-512x512.svg backend/app/static/icons/icon-512x512.png
    convert frontend/icons/icon-192x192.svg backend/app/static/icons/icon-192x192.png
    convert frontend/icons/icon-192x192.svg -resize 128x128 backend/app/static/icons/default.png
else
    echo -e "${YELLOW}ImageMagick not found - skipping icon generation${NC}"
fi

# Set up environment variables
echo -e "\n${BLUE}Setting up environment...${NC}"
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    # Generate a secure secret key
    SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
    sed -i "s/changeme-use-openssl-rand-hex-32/$SECRET_KEY/" backend/.env
    echo -e "${GREEN}Created new .env file with secure secret key${NC}"
else
    echo -e "${YELLOW}Using existing .env file${NC}"
fi

# Initialize database
echo -e "\n${BLUE}Initializing database...${NC}"
cd backend
python3 -c "from app.db.session import init_db; init_db()"
cd ..

# Function to start a service
start_service() {
    local name=$1
    local command=$2
    local port=$3
    local logfile=$4

    echo -e "\n${BLUE}Starting $name...${NC}"
    if check_port $port; then
        echo -e "${YELLOW}Port $port is in use. Attempting to free it...${NC}"
        fuser -k $port/tcp || true
        sleep 2
    fi

    nohup $command > "$logfile" 2>&1 &
    wait_for_service $port "$name"
}

# Create logs directory
mkdir -p logs

# Start backend
start_service "Backend server" \
    "cd backend && uvicorn main:app --host 0.0.0.0 --port 8010" \
    8010 \
    "logs/backend.log"

# Start frontend
start_service "Frontend server" \
    "cd frontend && python3 server.py" \
    8080 \
    "logs/frontend.log"

# Remove error trap
trap - EXIT

# Final status
echo -e "\n${GREEN}Setup Complete!${NC}"
echo -e "${BLUE}Services running:${NC}"
echo "- Frontend: http://localhost:8080"
echo "- Backend:  http://localhost:8010"
echo -e "\n${BLUE}Log files:${NC}"
echo "- Backend:  logs/backend.log"
echo "- Frontend: logs/frontend.log"
echo -e "\n${BLUE}Commands:${NC}"
echo "- View backend logs:  tail -f logs/backend.log"
echo "- View frontend logs: tail -f logs/frontend.log"
echo "- Stop servers:       ./stop.sh"
echo -e "\n${YELLOW}Note: Virtual environment is active. To deactivate, run: deactivate${NC}"
