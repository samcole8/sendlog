import yaml

class ConfigHandler:
    def __init__(self, path):
        self._path = path
        self._config = {}
        self.load()
    
    def load(self):
        with open(self._path, "r") as file:
            self._config = yaml.safe_load(file)
