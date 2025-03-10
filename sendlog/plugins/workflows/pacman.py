from plugin import LogType, Rule, Transformer

class Pacman(LogType):

    class RunCommand(Rule):

        def __call__(self, line):
            if "Running" in line:
                return True
            else:
                return False

        class Human(Transformer):
            def __call__(self, line):
                return line.split('] ', 2)[-1]

