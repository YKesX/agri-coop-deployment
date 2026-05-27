from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db import get_db
from models import Alert
from schemas import AlertOut

router = APIRouter()


@router.get("/alerts", response_model=list[AlertOut])
def list_alerts(
    resolved: bool = Query(False),
    db: Session = Depends(get_db),
):
    q = db.query(Alert)
    if resolved:
        q = q.filter(Alert.resolved_at.isnot(None))
    else:
        q = q.filter(Alert.resolved_at.is_(None))
    return q.order_by(Alert.created_at.desc()).all()


@router.get("/alerts/{alert_id}", response_model=AlertOut)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    a = db.query(Alert).filter(Alert.id == alert_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Alert not found")
    return a


@router.post("/alerts/{alert_id}/resolve", response_model=AlertOut)
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    a = db.query(Alert).filter(Alert.id == alert_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Alert not found")
    a.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(a)
    return a
