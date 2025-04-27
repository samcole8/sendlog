"""Sendlog Channel plugin module for Twilio SMS."""

from plugin import Channel

from twilio.rest import Client

class TwilioSMS(Channel):
    """Channel plugin class for Twilio SMS.
    
    required_vars:
        - account_sid: Twilio account SID.
        - auth_token: Twilio auth token.
        - sender: Sender's phone number (with country code).
        - recipient: Recipient's phone number (with country code).
        - timeout: Timeout duration (in seconds) for establishing the connection. 
    """
    __slots__ = ["account_sid", "auth_token", "sender", "recipient", "timeout"]
    def __call__(self, payload):
        # Set up SMS objects
        client = Client(self.account_sid, self.auth_token)
        client.http_client.timeout = self.timeout
        message = client.messages \
                        .create(
                            body=payload,
                            from_=self.sender,
                            to=self.recipient
                        )
