# main.py
import json
from datetime import datetime

import redis
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db import conn, cursor

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Redis ──────────────────────────────────────────────────────────────────────
r = redis.Redis(host="localhost", port=6379, decode_responses=True)


# ── Models ─────────────────────────────────────────────────────────────────────
class Signal(BaseModel):
    component_id: str
    severity: str
    message: str


class RCA(BaseModel):
    work_item_id: int
    root_cause: str
    fix: str
    prevention: str


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.get("/")
def home():
    return {"message": "IMS running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/signal")
def ingest_signal(signal: Signal):
    r.lpush("signal_queue", json.dumps(signal.dict()))
    return {"status": "queued"}


@app.get("/queue")
def check_queue():
    return {"length": r.llen("signal_queue")}


@app.get("/incidents")
def get_incidents():
    cursor.execute("SELECT * FROM work_items ORDER BY id DESC")
    rows = cursor.fetchall()

    incidents = []
    for row in rows:
        incidents.append({
            "id": row[0],
            "component_id": row[1],
            "severity": row[2],
            "status": row[3],
            "start_time": str(row[4]),
        })

    return {"incidents": incidents}


@app.post("/rca")
def submit_rca(rca: RCA):
    try:
        cursor.execute(
            "INSERT INTO rca (work_item_id, root_cause, fix, prevention)"
            " VALUES (%s, %s, %s, %s)",
            (rca.work_item_id, rca.root_cause, rca.fix, rca.prevention),
        )
        conn.commit()
        return {"status": "RCA submitted"}
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}


@app.post("/close/{id}")
def close_incident(id: int):
    try:
        cursor.execute(
            "SELECT status, start_time FROM work_items WHERE id = %s", (id,)
        )
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Incident not found")

        status, start_time = result

        if status == "CLOSED":
            raise HTTPException(status_code=400, detail="Incident already closed")

        cursor.execute("SELECT 1 FROM rca WHERE work_item_id = %s", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail="RCA required before closing")

        end_time = datetime.now()
        mttr = end_time - start_time

        cursor.execute(
            "UPDATE work_items SET status = %s WHERE id = %s",
            ("CLOSED", id),
        )
        conn.commit()

        return {"status": "Incident closed", "mttr_seconds": mttr.total_seconds()}

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}