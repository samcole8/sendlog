from sendlog import Sendlog, Msg
from sendlog.sinks.telegram import Telegram
from sendlog.sources.file import FileSource

sendlog = Sendlog()
telegram = Telegram(token="token", chat_id="chat_id")

@sendlog.watch(source=pacman_log, sinks=[telegram])
def on_pacman_command(msg):
    if not msg.match(r"^\[pacman\]"):
        return
    if match := msg.match(r"Running '(?P<command>[^']+)'"):
        return f"Command detected: {match.group('command')}"

sendlog.run()