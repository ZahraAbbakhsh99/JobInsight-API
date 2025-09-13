import threading
from app.services.email import send_email

def send_email_async(to: str, subject: str, body: str):
    threading.Thread(target=send_email, args=(to, subject, body)).start()
