# agents/whatsapp_utils.py
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
DEST_WHATSAPP_NUMBER = os.getenv("DEST_WHATSAPP_NUMBER")

def enviar_whatsapp(mensaje):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=mensaje,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=DEST_WHATSAPP_NUMBER
        )
        print(f"WhatsApp enviado. SID: {message.sid}")
        return "WhatsApp enviado correctamente."
    except Exception as e:
        print(f"Error al enviar WhatsApp: {e}")
        return f"Error al enviar WhatsApp: {e}"
