"""Sendlog Channel plugin module for SMTP services."""

from plugin import Channel

from email.mime.text import MIMEText
import smtplib
import ssl
from email.mime.text import MIMEText

class SMTP(Channel):
    """Channel plugin class for SMTP services.
    
    required_vars:
        - ip: SMTP server IP address or hostname.
        - port: Port number for SMTP connection (e.g., 465 for SSL, 587 for TLS).
        - username: Username for SMTP authentication (usually email).
        - password: Password for SMTP account authentication.
        - sender: Sender's email address.
        - recipient: Recipient's email address.
        - timeout: Timeout duration (in seconds) for establishing the SMTP connection. 
    """
    __slots__ = ["ip", "port", "username", "password", "sender", "recipient", "timeout"]
    def __call__(self, payload):

        # Extract information from payload
        subject = payload.get("subject", None)
        body = payload["body"]

        # Build email
        email = MIMEText(body)
        email["Subject"] = subject
        email["From"] = self.sender
        
        # Inititate SSL and connect to SMTP Server
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.ip, self.port, context=context, timeout=self.timeout) as server:
            # Log in and send email
            server.login(self.username, self.password)
            server.sendmail(self.sender, self.recipient, email.as_string())
