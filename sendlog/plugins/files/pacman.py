from plugin import Log, Rule, Transformation

class Pacman(Log):

    class RunCommand(Rule):
        def evaluate(self, line):
            if "Running" in line:
                return True
            else:
                return False

        class Human(Transformation):
            def transform(self, line):
                return line.split('] ', 2)[-1]
