# server/main.py
import os
import json
from fastapi import FastAPI, Header, HTTPException, Depends, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import csv
from database import SessionLocal, engine, Base
import models, schemas
from fastapi.middleware.cors import CORSMiddleware

import os
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY not set in environment")

# create tables
Base.metadata.create_all(bind=engine)

# API_KEY = os.getenv("API_KEY", "secret-key")  # set in env for production

app = FastAPI(title="SysUtil Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],  # or ["GET", "POST"] if you want to restrict
    allow_headers=["*"],
)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/api/v1/report", dependencies=[Depends(require_api_key)])
def receive_report(payload: schemas.ReportPayload, db: Session = Depends(get_db)):
    """Receive a report from an agent. Will insert a report and update machines table."""
    # parse timestamp
    try:
        ts = datetime.fromisoformat(payload.timestamp.replace("Z", "+00:00"))
    except Exception:
        ts = datetime.utcnow()

    # insert report
    r = models.Report(machine_id=payload.machine_id, timestamp=ts, payload=json.dumps(payload.dict()))
    db.add(r)

    # upsert machine latest
    m = db.query(models.Machine).filter(models.Machine.machine_id == payload.machine_id).first()
    if not m:
        m = models.Machine(machine_id=payload.machine_id)
        db.add(m)
    m.hostname = payload.hostname
    m.os_name = payload.os.get("name") if payload.os else None
    m.os_version = payload.os.get("version") if payload.os else None
    m.last_seen = ts
    m.latest_payload = json.dumps(payload.dict())

    db.commit()
    return {"status": "ok"}

@app.get("/api/v1/machines", response_model=List[schemas.MachineOut])
def list_machines(
    os_name: Optional[str] = Query(None, description="Filter by OS name (e.g., Windows)"),
    issue: Optional[str] = Query(None, description="Filter by issue key (e.g., unencrypted, noav, outdated)"),
    db: Session = Depends(get_db)
):
    """
    Return the latest record for all machines. Optional filtering:
      - os_name=Windows
      - issue=unencrypted|noav|outdated|sleep
    Filtering is applied in Python by inspecting latest_payload.
    """
    machines = db.query(models.Machine).all()
    out = []
    for m in machines:
        payload = None
        if m.latest_payload:
            try:
                payload = json.loads(m.latest_payload)
            except:
                payload = None
        # If filtering by OS, skip mismatches
        if os_name and (not m.os_name or os_name.lower() not in (m.os_name or "").lower()):
            continue
        # If filtering by issue, evaluate rules
        if issue:
            # detect issues
            issues_found = []
            if payload and "checks" in payload:
                checks = payload["checks"]
                # rule: unencrypted if disk_encrypted.value is False
                d = checks.get("disk_encrypted", {})
                if isinstance(d, dict) and d.get("value") is False:
                    issues_found.append("unencrypted")
                # rule: noav if antivirus.present is False or falsy
                av = checks.get("antivirus", {})
                if isinstance(av, dict) and av.get("present") in (False, None):
                    issues_found.append("noav")
                # rule: outdated if os_up_to_date.value is False
                outc = checks.get("os_up_to_date", {})
                if isinstance(outc, dict) and outc.get("value") is False:
                    issues_found.append("outdated")
                # rule: sleep if inactivity_sleep_minutes > 10
                sleep = checks.get("inactivity_sleep_minutes", {})
                # sleep may be dict or number
                try:
                    sv = sleep.get("value") if isinstance(sleep, dict) else sleep
                    if isinstance(sv, (int, float)) and sv > 10:
                        issues_found.append("sleep")
                except Exception:
                    pass
            if issue not in issues_found:
                continue
        out.append({
            "machine_id": m.machine_id,
            "hostname": m.hostname,
            "os_name": m.os_name,
            "os_version": m.os_version,
            "last_seen": m.last_seen.isoformat() if m.last_seen else None,
            "latest_payload": payload
        })
    # print(out)
    return out

@app.get("/api/v1/machines/{machine_id}")
def machine_history(machine_id: str, limit: int = 50, db: Session = Depends(get_db)):
    """Return history of reports for a machine (most recent first)."""
    rows = db.query(models.Report).filter(models.Report.machine_id == machine_id).order_by(models.Report.timestamp.desc()).limit(limit).all()
    out = []
    for r in rows:
        try:
            payload = json.loads(r.payload)
        except:
            payload = None
        out.append({
            "id": r.id,
            "machine_id": r.machine_id,
            "timestamp": r.timestamp.isoformat(),
            "payload": payload
        })
    print(out)
    return out

@app.get("/api/v1/export.csv", dependencies=[Depends(require_api_key)])
def export_csv(db: Session = Depends(get_db)):
    """
    Export latest status for all machines as CSV.
    Columns: machine_id,hostname,os_name,os_version,last_seen,disk_encrypted,os_up_to_date,av_present,inactivity_sleep_minutes
    """
    machines = db.query(models.Machine).all()

    def generator():
        header = ["machine_id","hostname","os_name","os_version","last_seen","disk_encrypted","os_up_to_date","av_present","inactivity_sleep_minutes"]
        out = []
        csv_w = csv.writer
        # write header
        yield ",".join(header) + "\n"
        for m in machines:
            disk = ""
            os_up = ""
            av = ""
            sleep = ""
            if m.latest_payload:
                try:
                    p = json.loads(m.latest_payload)
                    checks = p.get("checks", {})
                    d = checks.get("disk_encrypted", {})
                    disk = str(d.get("value")) if isinstance(d, dict) else str(d)
                    os_up = str(checks.get("os_up_to_date", {}).get("value"))
                    av = str(checks.get("antivirus", {}).get("present"))
                    s = checks.get("inactivity_sleep_minutes", {})
                    if isinstance(s, dict):
                        sleep = str(s.get("value"))
                    else:
                        sleep = str(s)
                except Exception:
                    pass
            row = [m.machine_id, m.hostname or "", m.os_name or "", m.os_version or "", m.last_seen.isoformat() if m.last_seen else "", disk, os_up, av, sleep]
            # proper CSV quoting:
            yield ",".join('"%s"' % (str(x).replace('"','""')) for x in row) + "\n"

    return StreamingResponse(generator(), media_type="text/csv", headers={"Content-Disposition":"attachment; filename=export.csv"})

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)