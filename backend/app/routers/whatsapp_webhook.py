import logging
import re
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Form, Request, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.models.alerts import Alert
from app.models.contacts import Contact
from app.models.weather import WeatherObservation
from app.models.whatsapp import WhatsAppMessage
from app.models.subscribers import Subscriber
from app.whatsapp_bot import whatsapp_bot
from app.websocket_manager import ws_manager

logger = logging.getLogger("WHATSAPP_WEBHOOK")
router = APIRouter(tags=["WhatsApp Webhook & Bot"])

CITIZEN_MENU_HI = (
    "🛡️ *TERRA SHIELD आपदा सेवा केंद्र*\n\n"
    "कृपया संख्या लिखकर उत्तर दें:\n"
    "1️⃣ निकटतम चेतावनी (Alerts near me)\n"
    "2️⃣ मौसम पूर्वानुमान (Weather)\n"
    "3️⃣ आपातकालीन हेल्पलाइन (Helplines)\n"
    "4️⃣ सुरक्षित आश्रय केंद्र (Nearest shelter)\n"
    "5️⃣ समस्या दर्ज करें (Report an issue)\n\n"
    "📍 निकटतम जानकारी के लिए अपनी लोकेशन पिन भेजें।"
)

CITIZEN_MENU_EN = (
    "🛡️ *TERRA SHIELD Disaster Advisory Service*\n\n"
    "Please reply with a number:\n"
    "1️⃣ Alerts near me\n"
    "2️⃣ Weather conditions\n"
    "3️⃣ Emergency helplines\n"
    "4️⃣ Nearest shelter\n"
    "5️⃣ Report an incident\n\n"
    "📍 Or share your live GPS location pin for localized status."
)

@router.post("/webhook/whatsapp")
async def whatsapp_incoming_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(""),
    Latitude: Optional[float] = Form(None),
    Longitude: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Unified Webhook for WhatsApp incoming messages (Twilio Sandbox / Meta Cloud API / Mock).
    Handles both Sarpanch Ground-Truth Verification and Citizen Numbered Menu Bot.
    """
    clean_body = Body.strip()
    phone_clean = From.replace("whatsapp:", "").strip()

    # 1. Check if this is a reply to an active Sarpanch verification request
    latest_open_alert = (
        db.query(Alert)
        .filter(Alert.ground_truth == "unverified", Alert.severity == "critical")
        .order_by(desc(Alert.node_timestamp))
        .first()
    )

    is_sarpanch_reply = False
    verdict_str = "UNCERTAIN"
    confidence_val = 0.50

    # NLP check if text indicates ground truth confirmation/denial
    status_parsed, conf_parsed = whatsapp_bot.analyze_response_nlp(clean_body)
    if status_parsed in ["CONFIRMED", "FALSE_ALARM"]:
        is_sarpanch_reply = True
        verdict_str = "CONFIRMED" if status_parsed == "CONFIRMED" else "DENIED"
        confidence_val = conf_parsed

    if is_sarpanch_reply and latest_open_alert:
        latest_open_alert.ground_truth = "confirmed" if verdict_str == "CONFIRMED" else "denied"
        db.commit()

        # Log message
        msg_record = WhatsAppMessage(
            direction="inbound",
            body=clean_body,
            parsed_intent="SARPANCH_VERIFICATION",
            verdict=verdict_str,
            confidence=confidence_val,
            alert_id=latest_open_alert.id,
            ts=datetime.utcnow()
        )
        db.add(msg_record)
        db.commit()

        # Broadcast update over WebSocket
        await ws_manager.broadcast("whatsapp_message", {
            "type": "SARPANCH_VERIFICATION",
            "alert_id": latest_open_alert.id,
            "verdict": verdict_str,
            "confidence": confidence_val,
            "body": clean_body,
            "ground_truth": latest_open_alert.ground_truth
        })

        reply_text = (
            f"✅ धन्यवाद। आपकी पुष्टि दर्ज कर ली गई है ({verdict_str}, {int(confidence_val*100)}% विश्वसनीयता)। "
            "NDRF एवं आपातकालीन नियंत्रण कक्ष को सूचित कर दिया गया है।"
        )
        return generate_twiml_response(reply_text)

    # 2. Numbered Citizen Menu Bot
    if clean_body == "1":
        # 1. Alerts near me
        active_alerts = db.query(Alert).filter(Alert.status.in_(["open", "acknowledged"])).limit(3).all()
        if active_alerts:
            alerts_text = "\n".join([f"⚠️ {a.hazard_type.upper()}: {a.message} (विश्वसनीयता: {int(a.confidence*100)}%)" for a in active_alerts])
            reply = f"🚨 *सक्रिय आपदा चेतावनियाँ:*\n\n{alerts_text}\n\nसुरक्षित रहें और ऊंचे स्थानों पर बने रहें।"
        else:
            reply = "✅ आपके क्षेत्र में वर्तमान में कोई आपातकालीन आपदा चेतावनी सक्रिय नहीं है। स्थिति सामान्य है।"

    elif clean_body == "2":
        # 2. Weather
        reply = "⛅ *ऋषिकेश-गढ़वाल मौसम स्थिति:*\nतापमान: 26.8°C | आर्द्रता: 64% | वर्षा: 0.0 मिमी | हवा: 12 किमी/घंटा\nजोखिम स्तर: निम्न (Low)"

    elif clean_body == "3":
        # 3. Helplines
        reply = "📞 *आपातकालीन हेल्पलाइन नंबर:*\n- राष्ट्रीय आपातकाल: 112\n- NDRF आपदा राहत: 011-24363260\n- SDRF उत्तराखंड: 1070 / 1077\n- अग्निशामक: 101\n- एम्बुलेंस: 108"

    elif clean_body == "4":
        # 4. Nearest shelter
        shelters = db.query(Contact).filter(Contact.category == "shelter").limit(2).all()
        s_text = "\n".join([f"🏠 *{s.name}*\nक्षमता: {s.capacity or 400} | फोन: {s.phone}" for s in shelters])
        reply = f"📍 *निकटतम सुरक्षित राहत शिविर:*\n\n{s_text}"

    elif clean_body == "5":
        # 5. Report issue
        reply = "📝 आपकी रिपोर्ट दर्ज की जा रही है। कृपया खतरे की सटीक जगह, जलस्तर, या फोटो भेजें। हमारी टीम जांच कर रही है।"

    else:
        # Default menu
        reply = CITIZEN_MENU_HI

    # Log citizen message
    msg_record = WhatsAppMessage(
        direction="inbound",
        body=clean_body,
        parsed_intent="CITIZEN_MENU",
        ts=datetime.utcnow()
    )
    db.add(msg_record)
    db.commit()

    return generate_twiml_response(reply)

def generate_twiml_response(message_body: str) -> Response:
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{message_body}</Message>
</Response>"""
    return Response(content=twiml, media_type="application/xml")
