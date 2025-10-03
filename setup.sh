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

# Install system dependencies
echo "Installing system dependencies..."
apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    imagemagick \
    libsqlite3-dev
check_status "System dependencies installed"

# Create project structure
echo "Setting up project structure..."
INSTALL_DIR=/opt/streetpass
mkdir -p $INSTALL_DIR/{backend,frontend,avatars}
chmod -R 755 $INSTALL_DIR

# Create service user
echo "Creating service user..."
useradd -r -s /bin/false streetpass
chown -R streetpass:streetpass $INSTALL_DIR
check_status "Service user created"

# Set up logging
mkdir -p /var/log/streetpass
chown streetpass:streetpass /var/log/streetpass
check_status "Log directory created"

# Create Python virtual environment
echo "Setting up Python virtual environment..."
cd $INSTALL_DIR
python3.11 -m venv backend/venv
source backend/venv/bin/activate
check_status "Virtual environment created"

# Install Python dependencies in one command
echo "Installing Python dependencies..."
pip install --no-cache-dir \
    fastapi \
    "uvicorn[standard]" \
    sqlalchemy \
    passlib[bcrypt] \
    "python-jose[cryptography]" \
    pillow \
    qrcode \
    pyjwt \
    pytest \
    httpx \
    python-multipart
check_status "Python dependencies installed"

# Copy application files
echo "Copying application files..."
cp -r * $INSTALL_DIR/
chmod +x $INSTALL_DIR/backend/*.sh
check_status "Files copied"

# Generate secret key and update config
echo "Generating secret key..."
SECRET_KEY=$(openssl rand -hex 32)
sed -i "s/changeme-use-os-urandom-in-production/$SECRET_KEY/" $INSTALL_DIR/backend/app/core/config.py
check_status "Secret key generated and configured"

# Install systemd services
echo "Installing systemd services..."
cp $INSTALL_DIR/backend/streetpass-backend.service /etc/systemd/system/
cp $INSTALL_DIR/frontend/streetpass-frontend.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable streetpass-backend
systemctl enable streetpass-frontend
check_status "Services installed"

# Start services
echo "Starting services..."
systemctl start streetpass-backend
systemctl start streetpass-frontend
check_status "Services started"

echo -e "\n${GREEN}Installation completed successfully!${NC}"
echo -e "${BLUE}StreetPass is now running:${NC}"
echo "- Backend API: http://localhost:8010"
echo "- Frontend: http://localhost:8080"
echo -e "\nTo check service status:"
echo "systemctl status streetpass-backend"
echo "systemctl status streetpass-frontend"
echo -e "\nView logs:"
echo "journalctl -u streetpass-backend -f"
echo "journalctl -u streetpass-frontend -f"