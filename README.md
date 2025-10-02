# StreetPass PWA

A lightweight "StreetPass"-style Progressive Web App with FastAPI backend.

## Project Structure

```
StreetPass/
├── backend/           # Python FastAPI backend
│   ├── app/          # Application code
│   ├── tests/        # Test files
│   ├── avatars/      # User avatar storage
│   ├── setup.sh      # Setup script
│   └── ...          # Other backend files
└── frontend/         # Static frontend files
    ├── index.html
    ├── app.js
    ├── styles.css
    ├── manifest.json
    └── icons/        # App icons
```

## Quick Start

1. Install Debian/Ubuntu system dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install python3.11 python3.11-venv python3-pip imagemagick libsqlite3-dev
   ```

2. Run the setup script:
   ```bash
   cd backend
   sudo ./setup.sh
   ```

This will:
- Install all dependencies
- Set up Python virtual environment
- Generate app icons
- Initialize database
- Start the server

The app will be available at http://localhost:8000

## Manual Setup

If you prefer to set up manually:

1. Set up the backend:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env  # Edit this file
   ./start-prod.sh
   ```

2. The frontend is static files served by the backend, no separate setup needed.

## Environment Variables
See `.env.example` for all options. Set `SECRET_KEY`, `DATABASE_URL`, allowed hosts, etc.

## Running
- Dev: `./run.sh`
- Prod: `./start-prod.sh` (systemd example in `streetpass.service`)

## Register via curl
```
curl -X POST http://localhost:8000/api/register -H 'Content-Type: application/json' -d '{"username":"alice","password":"strongpass"}'
```

## Tailscale
- Install Tailscale, join your network
- Use your Tailscale hostname for secure remote access
- HTTPS handled by Tailscale

## Backups
- Copy `streetpass.db` and `avatars/` directory

## Docker
- See `Dockerfile` for container usage

## Security
- Strong password policy, JWT, CORS, file size/type limits
- Rate limiting (simple in-memory)
- Do not expose to public internet without Tailscale or similar

## License
MIT
