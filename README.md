# StreetPass PWA

A lightweight "StreetPass"-style Progressive Web App with FastAPI backend.

## Architecture

- Backend: FastAPI + SQLite (runs on port 8010)
- Frontend: Custom Python HTTP server (runs on port 8080)
- Deployment: Systemd services with proper user isolation

## Installation

1. Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3-pip imagemagick libsqlite3-dev
```

2. Run the installation script:
```bash
sudo ./install.sh
```

This will:
- Create service user and directories
- Set up Python virtual environment
- Install dependencies
- Configure systemd services
- Generate secure keys
- Start both services

## Service Management

Backend service:
```bash
sudo systemctl status streetpass-backend
sudo systemctl restart streetpass-backend
sudo journalctl -u streetpass-backend -f
```

Frontend service:
```bash
sudo systemctl status streetpass-frontend
sudo systemctl restart streetpass-frontend
sudo journalctl -u streetpass-frontend -f
```

## Access

- Frontend: http://localhost:8080
- Backend API: http://localhost:8010
- Logs: /var/log/streetpass/

## Configuration

The `.env` file at `/opt/streetpass/.env` controls both services:
- Backend host/port
- Frontend host/port
- Database location
- JWT secrets
- CORS settings
- File size limits

## Security

- Services run as unprivileged 'streetpass' user
- Automatic port retry on conflicts
- Proper file permissions
- Separate log files
- Environment variable isolation

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
