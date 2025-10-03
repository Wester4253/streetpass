#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "Stopping StreetPass services..."

# Kill backend (uvicorn)
if pgrep -f "uvicorn main:app"; then
    pkill -f "uvicorn main:app"
    echo -e "${GREEN}Backend stopped${NC}"
else
    echo -e "${RED}Backend not running${NC}"
fi

# Kill frontend (Python HTTP server)
if pgrep -f "python3 server.py"; then
    pkill -f "python3 server.py"
    echo -e "${GREEN}Frontend stopped${NC}"
else
    echo -e "${RED}Frontend not running${NC}"
fi

echo -e "${GREEN}All services stopped${NC}"
