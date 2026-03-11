from sendlog import Sink

class Telegram(Sink):
    
    __slots__ = ["token", "chat_id"]