from typing import List, Optional
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import WhatsAppVerification, IncidentAlert
from app.schemas import WhatsAppVerificationResponse
from app.whatsapp_bot import whatsapp_bot
from app.websocket_manager import ws_manager

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp Human-as-a-Sensor Verification"])

@router.get("/verifications", response_model=List[WhatsAppVerificationResponse])
def list_verifications(incident_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Lists all vernacular WhatsApp verification queries sent to local Sarpanches."""
    query = db.query(WhatsAppVerification)
    if incident_id:
        query = query.filter(WhatsAppVerification.incident_id == incident_id)
    return query.order_by(desc(WhatsAppVerification.timestamp)).limit(20).all()

@router.post("/simulate-reply", response_model=dict)
async def simulate_sarpanch_reply(
    verification_id: int,
    reply_text: str,
    db: Session = Depends(get_db)
):
    """
    Hackathon Testbed: Simulates a Sarpanch replying via WhatsApp in vernacular (Hindi/English/Telugu).
    Executes NLP keyword/sentiment extraction, updates ground truth verification, and broadcasts to dashboard.
    """
    result = whatsapp_bot.process_incoming_reply(db, verification_id, reply_text)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    # Broadcast verification update via WebSockets
    await ws_manager.broadcast("WHATSAPP_VERIFICATION_UPDATE", result)

    return result

@router.post("/webhook")
async def twilio_whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Official Twilio WhatsApp Webhook endpoint.
    Processes live WhatsApp messages received from Sarpanches.
    """
    # Look for pending verification for this phone number
    verif = (
        db.query(WhatsAppVerification)
        .filter(WhatsAppVerification.verification_status == "PENDING")
        .order_by(desc(WhatsAppVerification.timestamp))
        .first()
    )

    if verif:
        result = whatsapp_bot.process_incoming_reply(db, verif.id, Body)
        await ws_manager.broadcast("WHATSAPP_VERIFICATION_UPDATE", result)
        
        reply_msg = (
            "धन्यवाद। आपकी रिपोर्ट दर्ज कर ली गई है। NDRF टीम को अलर्ट कर दिया गया है।"
            if result["status"] == "CONFIRMED"
            else "धन्यवाद। सूचना दर्ज कर ली गई है।"
        )
        # Twilio XML response
        from fastapi.responses import Response
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{reply_msg}</Message>
</Response>"""
        return Response(content=twiml, media_type="application/xml")

    return {"status": "received", "body": Body}
