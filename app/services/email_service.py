import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging
from typing import List

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SMTP"""

    def __init__(self):
        self.smtp_host = settings.MAIL_HOST
        self.smtp_port = settings.MAIL_PORT
        self.sender_email = settings.MAIL_USERNAME
        self.sender_password = settings.MAIL_PASSWORD
        self.sender_name = settings.MAIL_DISPLAY_NAME
        self.from_address = settings.MAIL_FROM

    def send_email(
        self,
        recipient_email: str,
        subject: str,
        html_content: str,
        text_content: str = None,
    ) -> bool:
        """
        Send an email to a single recipient

        Args:
            recipient_email: Email address of recipient
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text fallback content

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.sender_name} <{self.from_address}>"
            message["To"] = recipient_email

            # Attach plain text
            if text_content:
                message.attach(MIMEText(text_content, "plain"))

            # Attach HTML
            message.attach(MIMEText(html_content, "html"))

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            logger.info(f"Email sent successfully to {recipient_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
            return False

    def send_verification_email(self, recipient_email: str, verification_link: str) -> bool:
        """Send email verification link"""
        subject = "Verify Your Email Address"

        text_content = f"""
        Welcome! Please verify your email address by clicking the link below:
        {verification_link}

        This link will expire in 24 hours.

        If you did not create this account, please ignore this email.
        """

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .header {{
                    background-color: #007bff;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 0 0 5px 5px;
                }}
                .button {{
                    display: inline-block;
                    background-color: #007bff;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Verify Your Email</h1>
                </div>
                <div class="content">
                    <p>Welcome! Please verify your email address by clicking the button below:</p>
                    <a href="{verification_link}" class="button">Verify Email</a>
                    <p><strong>Or copy this link in your browser:</strong></p>
                    <p style="word-break: break-all;">{verification_link}</p>
                    <p><em>This link will expire in 24 hours.</em></p>
                    <p>If you did not create this account, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 {self.sender_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(recipient_email, subject, html_content, text_content)

    def send_verification_otp_email(self, recipient_email: str, otp: str) -> bool:
        """Send email verification OTP"""
        subject = "Your verification code"

        text_content = f"""
        Welcome! Use the following verification code to verify your email address:
        {otp}

        This code will expire shortly.

        If you did not create this account, please ignore this email.
        """

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .header {{
                    background-color: #007bff;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 0 0 5px 5px;
                    text-align: center;
                }}
                .code {{
                    font-size: 32px;
                    letter-spacing: 4px;
                    font-weight: bold;
                    background: #f0f0f0;
                    display: inline-block;
                    padding: 10px 20px;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Verify Your Email</h1>
                </div>
                <div class="content">
                    <p>Welcome! Use the verification code below to verify your email address:</p>
                    <div class="code">{otp}</div>
                    <p><em>This code will expire shortly.</em></p>
                    <p>If you did not create this account, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 {self.sender_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(recipient_email, subject, html_content, text_content)

    def send_password_reset_email(self, recipient_email: str, reset_link: str) -> bool:
        """Send password reset link"""
        subject = "Reset Your Password"

        text_content = f"""
        You requested a password reset. Click the link below to reset your password:
        {reset_link}

        This link will expire in 30 minutes.

        If you did not request this, please ignore this email and your password will remain unchanged.
        """

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .header {{
                    background-color: #dc3545;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 0 0 5px 5px;
                }}
                .button {{
                    display: inline-block;
                    background-color: #dc3545;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                    margin-top: 20px;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border: 1px solid #ffc107;
                    color: #856404;
                    padding: 10px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Reset Your Password</h1>
                </div>
                <div class="content">
                    <p>You requested a password reset. Click the button below to reset your password:</p>
                    <a href="{reset_link}" class="button">Reset Password</a>
                    <p><strong>Or copy this link in your browser:</strong></p>
                    <p style="word-break: break-all;">{reset_link}</p>
                    <p><em>This link will expire in 30 minutes.</em></p>
                    <div class="warning">
                        <strong>Security Notice:</strong> If you did not request this, please ignore this email and your password will remain unchanged.
                    </div>
                </div>
                <div class="footer">
                    <p>&copy; 2024 {self.sender_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(recipient_email, subject, html_content, text_content)

    def send_password_reset_otp_email(self, recipient_email: str, otp: str) -> bool:
        """Send password reset OTP"""
        subject = "Your password reset code"

        text_content = f"""
        You requested a password reset. Use the following code to reset your password:
        {otp}

        This code will expire shortly.

        If you did not request this, please ignore this email and your password will remain unchanged.
        """

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .header {{
                    background-color: #dc3545;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 0 0 5px 5px;
                    text-align: center;
                }}
                .code {{
                    font-size: 32px;
                    letter-spacing: 4px;
                    font-weight: bold;
                    background: #f0f0f0;
                    display: inline-block;
                    padding: 10px 20px;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Reset Your Password</h1>
                </div>
                <div class="content">
                    <p>You requested a password reset. Use the code below to reset your password:</p>
                    <div class="code">{otp}</div>
                    <p><em>This code will expire shortly.</em></p>
                    <p>If you did not request this, please ignore this email and your password will remain unchanged.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 {self.sender_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(recipient_email, subject, html_content, text_content)

    def send_welcome_email(self, recipient_email: str, name: str = "User") -> bool:
        """Send welcome email after successful registration"""
        subject = "Welcome to Our Service!"

        text_content = f"""
        Welcome, {name}!

        Your account has been created successfully. Your email has been verified and you can now log in to your account.

        Thank you for joining us!
        """

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .header {{
                    background-color: #28a745;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 0 0 5px 5px;
                }}
                .footer {{
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome, {name}!</h1>
                </div>
                <div class="content">
                    <p>Your account has been created successfully. Your email has been verified and you can now log in to your account.</p>
                    <p>Thank you for joining us!</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 {self.sender_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(recipient_email, subject, html_content, text_content)


# Create a singleton instance
email_service = EmailService()
