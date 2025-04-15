from plugin import LogType, Rule, Transformer

from datetime import datetime

class Pacman(LogType):
    regex = r"\[(?P<timestamp>.*?)\] \[(?P<application>.*?)\] (?P<message>.*)"

    class RunCommand(Rule):
        regex = r"Running\s+'(?P<command>[^']+)'"

        class HumanReadable(Transformer):
            def __call__(self, parts):
                context = parts["context"]
                timestamp = datetime.strptime(parts["timestamp"], "%Y-%m-%dT%H:%M:%S%z")
                return f"Command '{context["command"]}' detected at {timestamp.strftime("%Y-%m-%d %H:%M")}."
        
        class JSONL(Transformer):
            def __call__(self, parts):
                return parts