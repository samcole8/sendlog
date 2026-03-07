from sendlog.core import Transformer, Capture

class Auth(Capture):
    
    class Login(Capture):
        
        class ToTelegram(Transformer):
            pass