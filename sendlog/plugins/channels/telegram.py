from plugin import Channel

import requests

class Telegram(Channel):
    required_vars = ["chat_id", "token"]

    def __call__(self, msg):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        params = {"chat_id": self.chat_id, "text": msg}
        response = requests.post(url, params=params,)
