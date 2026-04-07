import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import winsound
import time as _time

def ses_cal():
    """Bilet bulununca dikkat çekici uyarı sesi çalar."""
    for _ in range(5):
        winsound.Beep(1000, 400)  # 1000 Hz, 400ms
        _time.sleep(0.1)
        winsound.Beep(1500, 400)  # 1500 Hz, 400ms
        _time.sleep(0.1)

def mail_gonder(baslik, icerik_html, alici_email):
    gonderici_email = "a@gmail.com" 
    sifre = "oiciuxhsskwqbrwf" 

    msg = MIMEMultipart()
    msg['From'] = gonderici_email
    msg['To'] = alici_email
    msg['Subject'] = baslik

    
    msg.attach(MIMEText(icerik_html, 'html', 'utf-8'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gonderici_email, sifre)
        server.send_message(msg)
        server.quit()
        print(f"📧 Acil Fırsat Maili Gönderildi: {alici_email}")
    except Exception as e:
        print(f"❌ Mail Gönderme Hatası: {e}")