Project: StreetPass-Like PWA (Full Production Copy)

Goal:
Generate a complete, production-ready repository that implements a lightweight "StreetPass-style" app. The repo must be fully working out of the box, secure by default, documented, and safe to run on an old laptop VM/LXC behind Tailscale. This is not a skeleton — produce full, runnable, tested code and all necessary project files.

High-level requirements:
- Single repo that contains both backend (API + avatar hosting) and frontend (PWA).
- Backend is Python 3.11+ using FastAPI and uvicorn (async).
- Use SQLite for persistence via SQLAlchemy ORM.
- Password-based user accounts (username + bcrypt-hashed password).
- JWT authentication for API; tokens stored client-side (localStorage) and included in API calls.
- QR-based friending flow (generate QR for user ID; scan QR to add friend).
- Avatars stored on disk in `avatars/` and served via the API.
- Frontend is a Progressive Web App (PWA) using plain HTML/CSS/vanilla JS (no heavy frameworks). Must be installable via "Add to Home Screen" on Safari/Chrome.
- Everything served from the same FastAPI app (static files + API endpoints).
- Project must include production-facing extras: requirements, README, .env.example, systemd service or run script, basic unit tests, and secure defaults (CORS, allowed hosts, file size limits, password policy).
- Keep it lightweight so it runs on a modest VM: 1 vCPU, 2GB RAM, 20GB disk.

Repo structure to produce:
- README.md (detailed instructions: setup, environment variables, Tailscale tips, running, backups, migrations)
- requirements.txt
- main.py (entrypoint; create app & include startup/shutdown hooks)
- app/
  - api/
    - auth.py (register / login / logout / token refresh)
    - users.py (profile, upload avatar, get avatar URL, qr endpoint)
    - friends.py (add friend, get friends list)
  - core/
    - config.py (load env vars; defaults; secrets from .env)
    - security.py (bcrypt helpers, JWT helpers)
  - db/
    - models.py (SQLAlchemy models: User, Friend)
    - session.py (engine, SessionLocal)
    - crud.py (DB access layer)
    - migrations/ (Alembic config optional but include simple migration or schema init)
  - static/ (frontend files)
    - index.html
    - app.js
    - styles.css
    - manifest.json
    - service-worker.js
    - icons/ (app icons)
- avatars/ (runtime directory created at first run)
- tests/
  - test_auth.py
  - test_friends.py
  - test_api_integration.py (simple integration)
- .env.example (sample ENV variables; SECRET_KEY, JWT settings, DATABASE_URL)
- dockerfile (optional, but include one)
- systemd service file example (to run uvicorn as service)
- helper scripts:
  - run.sh (dev run)
  - start-prod.sh (production run via uvicorn or uvicorn+gunicorn instructions)
- LICENSE (MIT)

Database schema (explicit):
- users table:
  - id: UUID primary key
  - username: unique text
  - password_hash: text
  - avatar_filename: nullable text (store `{id}.png` or path)
  - created_at: timestamp
- friends table:
  - id: integer PK
  - user_id: UUID -> users.id
  - friend_id: UUID -> users.id
  - added_at: timestamp
  - unique constraint on (user_id, friend_id)
  - Make friendships symmetric only if both sides add each other OR create mutual-link behavior: when user A adds B, create a record for A->B and B->A automatically.

Auth details:
- Use bcrypt for hashing (bcrypt package).
- Use PyJWT or jose to sign JWTs with a strong SECRET_KEY loaded from env.
- Access tokens expire (e.g. 1 day); include refresh token route if possible.
- All protected endpoints require Authorization header `Bearer <token>`.

API endpoints (complete list and behavior):
- POST /api/register
  - body: { username, password }
  - returns: { id, username, token }
  - rejects usernames that are taken; enforce min password length
- POST /api/login
  - body: { username, password }
  - returns: { token, user: { id, username, avatar_url } }
- GET /api/profile
  - auth required; returns user profile
- POST /api/upload-avatar
  - auth required; multipart/form-data file upload; validate content-type & size limit; write to avatars/{user_id}.png; return avatar_url
- GET /api/avatar/{user_id}
  - serve image file or default avatar
- GET /api/qr/{user_id}
  - generate QR PNG on-the-fly encoding the user's UUID (or a JSON payload containing id+username signature). Return PNG image.
- POST /api/add-friend
  - auth required; body: { friend_id } (scanned from QR)
  - validate friend exists; create mutual friendship records; return updated friend list
- GET /api/friends
  - auth required; list friends with username, avatar_url, added_at
- GET /api/health
  - returns OK for monitoring

Frontend requirements (PWA):
- index.html with a simple SPA-style UI (tabs / nav):
  - Setup/Server page: enter server URL (save to localStorage), register/login
  - Profile page: show username, avatar, "Show my QR" button that fetches /api/qr/{id}
  - Scan page: open camera using navigator.mediaDevices.getUserMedia; use a JS QR library (e.g. jsQR) to scan frames and extract friend_id; call /api/add-friend
  - Friends page: GET /api/friends and render avatars + added_at
- Use fetch() for API calls; include Authorization header after login.
- Save token and user id in localStorage. Auto-check session on load.
- manifest.json and service-worker.js enabling offline shell caching of static resources, with network-first for API calls.
- Friendly error handling for CORS, offline, and invalid QR scanning.

Security & production best practices:
- Do not log passwords. Log events with caution.
- Rate-limit endpoints (simple in-memory rate limiter or note in README).
- Validate uploaded file types and limit size (e.g., 500 KB).
- CORS: allow origins based on env variable or default to localhost + tailscale domain; do not open to all in production.
- Use strong SECRET_KEY in .env; provide .env.example with placeholders.
- Recommend running behind Tailscale and using the tailscale hostname (HTTPS handled by Tailscale).
- Provide instructions for backups (copy db file & avatars).

Testing & docs:
- Include unit tests for auth and friend logic (pytest).
- README must include:
  - setup steps (create venv, pip install -r requirements.txt)
  - env vars explanation (.env.example)
  - how to run dev and prod
  - how to register a user via curl
  - how to configure Tailscale and point device to the machine
  - marketplace: optional Docker usage and systemd example
  - security caveats

Deliverable:
- Produce all files listed above, with full content (not placeholders), ready-to-run code. Where external assets are needed (icons), generate simple SVG/PNG placeholders and include them.
- The code should be well-commented, idiomatic, and include error handling.

When generating code, make sure to:
- Create the SQLite DB and tables automatically on first run if missing.
- Create avatars/ dir automatically.
- Provide clear console output when server starts showing the URL and that it's ready.
- Keep the frontend minimal but polished enough for testing on mobile Safari (touch targets, responsive layout).

Now generate the entire repository contents (all files listed) in full. End of prompt.
