# AI Security Intelligence Platform MVP

This is a local-only monorepo for the AI Security MVP.

## Folder Structure
- `/backend`: FastAPI Python application
- `/frontend`: Next.js App Router application
- `/docs`: Documentation
- `/seed_data`: Example JSON exports from MISP and CISO Assistant

## Local Setup
1. Backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. Frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
