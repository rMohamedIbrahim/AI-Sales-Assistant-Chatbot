"""
Test Gmail API credentials and functionality
"""
import asyncio
import aiosmtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import os
from dotenv import load_dotenv

load_dotenv()

async def test_gmail_api():
    """Test Gmail SMTP credentials"""
    print("🧪 Testing Gmail API Credentials...")
    
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    print(f"📧 SMTP Server: {smtp_server}:{smtp_port}")
    print(f"👤 Username: {smtp_username}")
    print(f"🔐 Password: {'*' * len(smtp_password) if smtp_password else 'NOT SET'}")
    
    if not smtp_username or not smtp_password:
        print("❌ SMTP credentials not configured")
        return False
    
    try:
        # Test SMTP connection
        print("\n🔗 Testing SMTP connection...")
        
        # Create message
        message = MimeMultipart()
        message["From"] = smtp_username
        message["To"] = smtp_username  # Send to self for testing
        message["Subject"] = "VoiceBot Test - SMTP Working"
        
        body = """
        🎉 Congratulations! Your VoiceBot SMTP configuration is working perfectly.
        
        This test email confirms that:
        ✅ Gmail SMTP credentials are valid
        ✅ App password is configured correctly
        ✅ Email notifications will work in your VoiceBot application
        
        Your VoiceBot Enterprise system is ready for production!
        
        Best regards,
        VoiceBot Enterprise System
        """
        
        message.attach(MimeText(body, "plain"))
        
        # Send email
        async with aiosmtplib.SMTP(hostname=smtp_server, port=smtp_port) as server:
            await server.starttls()
            await server.login(smtp_username, smtp_password)
            await server.send_message(message)
        
        print("✅ SMTP test successful! Test email sent.")
        print(f"📬 Check your inbox at {smtp_username}")
        return True
        
    except Exception as e:
        print(f"❌ SMTP test failed: {str(e)}")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure you're using an App Password, not your regular Gmail password")
        print("2. Enable 2-Factor Authentication in your Google account")
        print("3. Generate App Password: Google Account > Security > App passwords")
        print("4. Use the 16-character app password (with spaces removed)")
        return False

if __name__ == "__main__":
    asyncio.run(test_gmail_api())
