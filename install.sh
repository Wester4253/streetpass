#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

echo -e "${BLUE}StreetPass Installation Script${NC}"
echo "------------------------"

# Create streetpass user
echo "Creating service user..."
useradd -r -s /bin/false streetpass 2>/dev/null || true

# Create necessary directories
echo "Creating directories..."
mkdir -p /opt/streetpass/{backend,frontend}
mkdir -p /var/log/streetpass
mkdir -p /opt/streetpass/backend/avatars

# Copy files
echo "Copying files..."
cp -r backend/* /opt/streetpass/backend/
cp -r frontend/* /opt/streetpass/frontend/

# Set up Python environment
echo "Setting up Python environment..."
cd /opt/streetpass/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up environment file
if [ ! -f /opt/streetpass/.env ]; then
    echo "Creating .env file..."
    cp .env.example /opt/streetpass/.env
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/changeme-use-openssl-rand-hex-32/$SECRET_KEY/" /opt/streetpass/.env
fi

# Set permissions
echo "Setting permissions..."
chown -R streetpass:streetpass /opt/streetpass
chown -R streetpass:streetpass /var/log/streetpass
chmod 755 /opt/streetpass/frontend/server.py

# Install systemd services
echo "Installing systemd services..."
cp /opt/streetpass/backend/streetpass-backend.service /etc/systemd/system/
cp /opt/streetpass/frontend/streetpass-frontend.service /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Start services
echo "Starting services..."
systemctl enable streetpass-backend streetpass-frontend
systemctl start streetpass-backend streetpass-frontend

# Show status
echo -e "\n${BLUE}Service Status:${NC}"
systemctl status streetpass-backend --no-pager
echo -e "\n${BLUE}Frontend Status:${NC}"
systemctl status streetpass-frontend --no-pager

echo -e "\n${GREEN}Installation complete!${NC}"
echo "Access the application at:"
echo "Frontend: http://localhost:8080"
echo "Backend API: http://localhost:8010"
echo -e "\nLogs are in /var/log/streetpass/"
echo "Use these commands to manage services:"
echo "systemctl restart streetpass-backend"
echo "systemctl restart streetpass-frontend"
echo "systemctl status streetpass-{backend,frontend}"
