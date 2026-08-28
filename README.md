# TrustTrack

Hackathon scaffold (~15%): unique donation tracking IDs and NGO proof upload. Image authenticity (ELA, perceptual hash, EXIF), aid-type matching, trust scores, and donor Q&A are not built yet.

## Run locally

Postgres (preferred, when Docker Desktop is running):

```bash
docker compose up -d
cd backend
copy .env.example .env
```

Without Docker, point `backend/.env` at SQLite instead:

```
DATABASE_URL=sqlite:///./trusttrack.db
UPLOAD_DIR=uploads
CORS_ORIGINS=http://localhost:5173
```

Then start the API:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API: http://localhost:8000  
Docs: http://localhost:8000/docs  
Health: `GET /health`

Frontend (new terminal):

```bash
cd frontend
copy .env.example .env
npm install
npm run dev
```

Open http://localhost:5173 — create a donation, copy the tracking ID, upload a proof photo, and confirm the stored record.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Liveness |
| POST | `/donations` | Create donation, return `TT-XXXXXXXX` tracking ID |
| GET | `/donations/{tracking_id}` | Fetch donation + proofs |
| POST | `/donations/{tracking_id}/proof` | Multipart image + claimed GPS / time / aid type |

Startup seeds `Alkhidmat Demo NGO` and `Demo Donor`. Proofs land in `backend/uploads/` with `verification_status=pending`.

## Repository link (hackathon form)

This field is optional. Create a **public** GitHub repo from this folder only (not from your user home directory), push, and paste that URL. Leave the form blank until the repo is public.
