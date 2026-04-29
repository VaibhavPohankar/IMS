# 🚨 IMS — Incident Management System

A lightweight Incident Management System that ingests error signals 
from distributed components, deduplicates them, creates incidents, and enforces
root cause analysis before closure.

Designed to simulate real-world SRE workflows such as alert deduplication,
incident lifecycle management, and post-incident analysis.

---

## Tech Stack

- FastAPI — REST API  
- Redis — signal queue  
- PostgreSQL — incident storage  
- Python worker — queue consumer with debounce logic  
- React (Vite) — minimal dashboard UI  

---

## Architecture

Client
  │
  │  POST /signal
  ▼
FastAPI  ──────────►  Redis Queue
                           │
                           ▼
                        Worker
                     (debounce 10s)
                           │
                           ▼
                       PostgreSQL
                      (work_items)
                           │
                           ▼
              FastAPI  (/incidents /rca /close)
                           ▲
                           │
                   React Dashboard

---

## How It Works

1. Signal ingestion — `/signal` pushes events to Redis  
2. Worker processing — groups signals within 10s into one incident  
3. Incident lifecycle — OPEN → INVESTIGATING → RESOLVED → CLOSED  
4. RCA enforcement — cannot close without RCA  
5. MTTR — calculated on closure  

---

## Project Structure

IMS/
├── backend/
│   ├── main.py
│   ├── worker.py
│   └── ...
├── frontend/
│   └── src/
├── docker-compose.yml
├── .env.example
└── requirements.txt
---

## Setup

### Prerequisites
- Python 3.11+
- Node.js
- Docker

---

### Install backend

pip install -r requirements.txt

---

### Configure environment (.env)

DB_HOST=localhost  
DB_PORT=5432  
DB_NAME=ims_db  
DB_USER=postgres  
DB_PASSWORD=your_password  

REDIS_HOST=localhost  
REDIS_PORT=6379  

---

### Start services

docker-compose up -d

---

### Run backend

uvicorn main:app --reload

---

### Run worker

python worker.py

---

### Run frontend

cd frontend  
npm install  
npm run dev  

---

## API Endpoints

GET /health  
POST /signal  
GET /incidents  
PATCH /incidents/{id}/status  
POST /rca  
POST /close/{id}  

---

## Frontend (Dashboard)

- Auto-refresh incident list (5s)
- Click to view details
- Submit RCA
- Close incident

---

## Key Features

- Redis queue for ingestion  
- Debounce logic  
- Incident lifecycle control  
- RCA required before closure  
- MTTR calculation  
- Decoupled processing  
- No hardcoded credentials  

---

## Notes

Frontend is intentionally minimal — focus is on backend system design.

## Screenshots

### Dashboard
![Dashboard](Screenshots/dashboard.png)

### Incident Detail
![Incident](Screenshots/incident.png)

### API Docs
![API](Screenshots/api.png)