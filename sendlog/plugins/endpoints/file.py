"""Log your logs."""

from plugin import Endpoint

class File(Endpoint):
    required_vars = ["path"]

    def __call__(self, msg):
        with open(self.path, "a") as file:
            file.write(msg)