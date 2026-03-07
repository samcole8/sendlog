from sendlog.core import Monitor, Source, run
from sendlog.plugins.formats.auth import Auth
from sendlog.plugins.sinks.telegram import Telegram

telegram = Telegram()

class Monitor1(Monitor):
    source = "file.txt"
    flows = [
        Auth.Login.ToTelegram | telegram
    ]

run(Monitor1)