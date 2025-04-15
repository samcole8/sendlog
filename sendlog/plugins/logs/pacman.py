from plugin import LogType, Rule, Transformer

from datetime import datetime

class Pacman(LogType):
    regex = r"\[(?P<timestamp>.*?)\] \[(?P<application>.*?)\] (?P<message>.*)"

    class RunCommand(Rule):
        regex = r"Running\s+'(?P<command>[^']+)'"

        class HumanReadable(Transformer):
            def __call__(self, parts):
                context = parts["context"]
                return f"Command '{context["command"]}' detected at {parts["timestamp"]}."
        
        class JSONL(Transformer):
            def __call__(self, parts):
                return parts