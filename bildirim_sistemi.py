import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def mail_gonder(baslik, icerik_html, alici_email):
    gonderici_email = "safakkuru21@gmail.com" 
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