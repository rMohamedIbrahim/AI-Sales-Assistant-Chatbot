"""
Free Notification service for sending email notifications.
Uses SMTP (Gmail) for free email notifications instead of paid SMS services.
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import aiosmtplib
from src.core.config import get_settings
from typing import Dict, Any, Optional, List
import asyncio
import logging
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)
settings = get_settings()

class FreeNotificationService:
    """Notification service using free email services"""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.enabled = settings.ENABLE_EMAIL_NOTIFICATIONS and bool(self.smtp_username)
        
        if not self.enabled:
            logger.warning("Email notifications disabled - missing SMTP configuration")

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = False,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Send email notification using SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            is_html: Whether body is HTML content
            attachments: List of file paths to attach
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("Email notifications are disabled")
            return False

        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = self.smtp_username
            message["To"] = to_email
            message["Subject"] = subject

            # Add body to email
            if is_html:
                message.attach(MIMEText(body, "html"))
            else:
                message.attach(MIMEText(body, "plain"))

            # Add attachments if any
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        message.attach(part)

            # Send email using aiosmtplib
            await aiosmtplib.send(
                message,
                hostname=self.smtp_server,
                port=self.smtp_port,
                start_tls=True,
                username=self.smtp_username,
                password=self.smtp_password
            )

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    async def send_booking_confirmation(
        self,
        email: str,
        booking_details: Dict[str, Any]
    ) -> bool:
        """
        Send test drive booking confirmation email.
        
        Args:
            email: Customer email
            booking_details: Dictionary containing booking information
            
        Returns:
            True if email sent successfully
        """
        try:
            subject = "Test Drive Booking Confirmation - Two Wheeler Sales"
            
            body = f"""
Dear Customer,

Your test drive booking has been confirmed! Here are the details:

🚗 Booking Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Booking ID: {booking_details.get('id', 'N/A')}
🏍️ Vehicle Model: {booking_details.get('vehicle_model', 'N/A')}
📅 Date: {booking_details.get('preferred_date', 'N/A')}
📍 Location: {booking_details.get('location', 'N/A')}
⏰ Status: {booking_details.get('status', 'Confirmed')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Important Instructions:
• Please arrive 15 minutes before your scheduled time
• Bring a valid driving license
• Bring identity proof (Aadhar/PAN/Passport)
• Wear comfortable riding gear

📞 Need to reschedule or cancel?
Reply to this email or call our customer service.

Thank you for choosing our service!

Best regards,
Two Wheeler Sales Team
"""

            return await self.send_email(email, subject, body)

        except Exception as e:
            logger.error(f"Failed to send booking confirmation: {str(e)}")
            return False

    async def send_service_notification(
        self,
        email: str,
        service_details: Dict[str, Any]
    ) -> bool:
        """
        Send service-related notification email.
        
        Args:
            email: Customer email
            service_details: Dictionary containing service information
            
        Returns:
            True if email sent successfully
        """
        try:
            notification_type = service_details.get('type', 'update')
            
            if notification_type == 'confirmation':
                subject = "Service Request Confirmation - Two Wheeler Sales"
                body = f"""
Dear Customer,

Your service request has been received and confirmed!

🔧 Service Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Service ID: {service_details.get('id', 'N/A')}
🏍️ Vehicle Model: {service_details.get('vehicle_model', 'N/A')}
🔧 Service Type: {service_details.get('service_type', 'N/A')}
📅 Preferred Date: {service_details.get('preferred_date', 'N/A')}
📝 Description: {service_details.get('description', 'N/A')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Our team will contact you shortly to schedule the service.

Thank you for choosing our service!
"""
            
            elif notification_type == 'completion':
                subject = "Service Completed - Two Wheeler Sales"
                body = f"""
Dear Customer,

Great news! Your vehicle service has been completed.

🎉 Service Completion Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Service ID: {service_details.get('id', 'N/A')}
✅ Status: Completed
💰 Total Amount: ₹{service_details.get('amount', 0)}
📅 Completion Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your vehicle is ready for pickup. Please bring:
• Service receipt/ID
• Vehicle documents
• Payment (if pending)

Thank you for choosing our service!
"""
            
            elif notification_type == 'delay':
                subject = "Service Update - Slight Delay - Two Wheeler Sales"
                body = f"""
Dear Customer,

We regret to inform you about a slight delay in your service completion.

📢 Service Update:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Service ID: {service_details.get('id', 'N/A')}
⏰ Status: Delayed
📅 New Estimated Completion: {service_details.get('new_estimate', 'TBD')}
🔍 Reason: Technical complexity requires additional time
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

We apologize for any inconvenience caused. Our team is working diligently to complete your service as soon as possible.

We appreciate your patience and understanding.
"""
            
            else:
                subject = "Service Update - Two Wheeler Sales"
                body = service_details.get('message', 'Service update notification')

            return await self.send_email(email, subject, body)

        except Exception as e:
            logger.error(f"Failed to send service notification: {str(e)}")
            return False

    async def send_reminder(
        self,
        email: str,
        reminder_details: Dict[str, Any]
    ) -> bool:
        """
        Send reminder email for upcoming appointments.
        
        Args:
            email: Customer email
            reminder_details: Dictionary containing reminder information
            
        Returns:
            True if email sent successfully
        """
        try:
            reminder_type = reminder_details.get('type', 'booking')
            
            if reminder_type == 'booking':
                subject = "🔔 Reminder: Test Drive Tomorrow - Two Wheeler Sales"
                body = f"""
Dear Customer,

This is a friendly reminder about your test drive appointment tomorrow!

🚨 Reminder Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Booking ID: {reminder_details.get('booking_id', 'N/A')}
🏍️ Vehicle Model: {reminder_details.get('vehicle_model', 'N/A')}
📅 Date: {reminder_details.get('date', 'Tomorrow')}
⏰ Time: {reminder_details.get('time', 'N/A')}
📍 Location: {reminder_details.get('location', 'N/A')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Don't forget to bring:
• Valid driving license
• Identity proof
• Comfortable riding gear

Looking forward to seeing you tomorrow!
"""
            
            elif reminder_type == 'service':
                subject = "🔔 Service Reminder - Two Wheeler Sales"
                body = f"""
Dear Customer,

Reminder: Your vehicle service is scheduled for tomorrow.

🔧 Service Reminder:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Service ID: {reminder_details.get('service_id', 'N/A')}
🏍️ Vehicle Model: {reminder_details.get('vehicle_model', 'N/A')}
📅 Date: {reminder_details.get('date', 'Tomorrow')}
⏰ Time: {reminder_details.get('time', 'N/A')}
🔧 Service Type: {reminder_details.get('service_type', 'N/A')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please bring your vehicle and necessary documents.
"""
            
            else:
                subject = "Reminder - Two Wheeler Sales"
                body = reminder_details.get('message', 'Appointment reminder')

            return await self.send_email(email, subject, body)

        except Exception as e:
            logger.error(f"Failed to send reminder: {str(e)}")
            return False

    async def send_welcome_email(
        self,
        email: str,
        customer_name: str
    ) -> bool:
        """
        Send welcome email to new customers.
        
        Args:
            email: Customer email
            customer_name: Customer name
            
        Returns:
            True if email sent successfully
        """
        try:
            subject = "🎉 Welcome to Two Wheeler Sales!"
            
            body = f"""
Dear {customer_name},

Welcome to Two Wheeler Sales! We're excited to have you join our family.

🏍️ What We Offer:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚗 Test Drive Booking
🔧 Professional Service & Maintenance
💬 Multilingual Voice Support
🎯 Personalized Recommendations
🎁 Exclusive Offers & Deals
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌟 Your VoiceBot Experience:
Our intelligent VoiceBot can help you with:
• Book test drives in multiple languages
• Schedule service appointments
• Get vehicle information and recommendations
• Track your booking and service status

📞 Get Started:
Call our VoiceBot anytime or visit our website to explore our latest two-wheelers!

Thank you for choosing Two Wheeler Sales!

Best regards,
Two Wheeler Sales Team
"""

            return await self.send_email(email, subject, body)

        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
            return False

    async def send_feedback_request(
        self,
        email: str,
        interaction_details: Dict[str, Any]
    ) -> bool:
        """
        Send feedback request email after service completion.
        
        Args:
            email: Customer email
            interaction_details: Details about the completed interaction
            
        Returns:
            True if email sent successfully
        """
        try:
            subject = "📝 Your Feedback Matters - Two Wheeler Sales"
            
            body = f"""
Dear Customer,

Thank you for using our services! We hope you had a great experience.

📊 Help Us Improve:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏍️ Service: {interaction_details.get('service_type', 'Two Wheeler Sales')}
📅 Date: {interaction_details.get('date', datetime.now().strftime('%Y-%m-%d'))}
⭐ How was your experience?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your feedback helps us provide better service to all our customers.

Please reply to this email with:
1. Overall rating (1-5 stars)
2. What you liked most
3. Any suggestions for improvement

Thank you for your time and trust!

Best regards,
Two Wheeler Sales Team
"""

            return await self.send_email(email, subject, body)

        except Exception as e:
            logger.error(f"Failed to send feedback request: {str(e)}")
            return False

# Create singleton instance
notification_service = FreeNotificationService()
