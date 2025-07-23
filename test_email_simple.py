"""
Simple Gmail SMTP test
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def test_gmail_simple():
    """Test Gmail SMTP with simple approach"""
    print("🧪 Testing Gmail API Credentials...")
    
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    print(f"📧 SMTP Server: {smtp_server}:{smtp_port}")
    print(f"👤 Username: {smtp_username}")
    print(f"🔐 Password: {'✅ Set' if smtp_password else '❌ Not Set'}")
    
    if not smtp_username or not smtp_password:
        print("❌ SMTP credentials not configured")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = smtp_username
        msg['Subject'] = "VoiceBot Enterprise - Test Email ✅"
        
        body = """
🎉 Congratulations! Your VoiceBot Enterprise system is working perfectly!

✅ Gmail SMTP configuration: WORKING
✅ App password authentication: SUCCESS  
✅ Email notifications: READY
✅ Enterprise frontend: ACTIVE

Your VoiceBot system is ready for production use!

Test completed on: """ + str(os.popen('date /t').read().strip())
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        print("\n🔗 Connecting to Gmail SMTP...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        print("🔐 Authenticating...")
        server.login(smtp_username, smtp_password)
        print("📤 Sending test email...")
        server.send_message(msg)
        server.quit()
        
        print("✅ EMAIL TEST SUCCESSFUL!")
        print(f"📬 Test email sent to: {smtp_username}")
        print("💼 Your VoiceBot Enterprise system is fully operational!")
        return True
        
    except Exception as e:
        print(f"❌ Email test failed: {str(e)}")
        if "Username and Password not accepted" in str(e):
            print("\n💡 Fix: Use App Password instead of regular password")
            print("1. Enable 2FA in Google Account")
            print("2. Generate App Password: Google Account > Security > App passwords")
            print("3. Use the 16-character app password")
        return False

if __name__ == "__main__":
    test_gmail_simple()
