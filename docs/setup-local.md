# Local Setup Guide

Follow these steps to get the AI Security Intelligence Platform running locally on a fresh machine.

## Prerequisites
- **Python 3.10+** (Backend)
- **Node.js 18+ & npm** (Frontend)
- **MongoDB** (Local instance or Atlas URI)
- **Google Cloud Project** (With Vertex AI API enabled and `GOOGLE_APPLICATION_CREDENTIALS` set)

## 1. Environment Setup

### Backend
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set MONGODB_URI and GOOGLE_CLOUD_PROJECT
```

### Frontend
```powershell
cd frontend
npm install
cp .env.example .env.local
# Ensure NEXT_PUBLIC_API_BASE points to http://localhost:8000/api/v1
```

## 2. Initialize Seed Content

1. Start the backend: `python main.py`
2. Create the admin user: 
   - Visit `http://localhost:8000/api/v1/auth/seed-admin` (initializes `admin@platform.io` / `admin1234`)
3. Login via the UI (http://localhost:3000/login).
4. Go to **Settings** -> **Admin Console**.
5. Click **Reload Seed Foundation**. This ingestion phase populates:
   - Assets
   - Threats (MISP-style)
   - Policies (ISO/NIST)
   - Vulnerabilities (CVEs)
6. Click **Reconcile Knowledge Graph**. This correlates the entities.
7. Click **Re-index Vector Store**. This enables RAG for the Policy Advisor.

## 3. Start Development Servers

### Backend (Port 8000)
```powershell
uvicorn app.main:app --reload
```

### Frontend (Port 3000)
```powershell
npm run dev
```

Platform is now ready at [http://localhost:3000](http://localhost:3000).
