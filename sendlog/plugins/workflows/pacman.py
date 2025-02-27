from plugin import LogType, Rule, Transformer

class Pacman(LogType):

    class RunCommand(Rule):
        def evaluate(self, line):
            if "Running" in line:
                return True
            else:
                return False

        class Human(Transformer):
            def transform(self, line):
                return line.split('] ', 2)[-1]
