import yaml
from importlib import import_module

class ConfigHandler:
    """Initialises and stores objects referenced in the configuration file."""
    def __init__(self, path):
        self._path = path
        self._config = {}
        self.load_config()

    def load_config(self):
        with open(self._path, "r") as file:
            self._config = yaml.safe_load(file)

    def get_data(self):
        """
        Traverse the configuration file and yield information about every alert in the following format:

        (path, module_name, rule_name, transformation_name, endpoint_name)
        """
        
        def files():
            for path, file_config in self._config["files"].items():
                yield path, file_config["plugin"], file_config["format"], file_config
        
        def rules(file_config):
            for rule_name, rule_config in file_config["rules"].items():
                yield rule_name, rule_config
        
        def transformations(rule_config):
            for transformation_name, transformation_config in rule_config["transformations"].items():
                yield transformation_name, transformation_config
        
        def endpoints(transformation_config):
            for endpoint_name in transformation_config["endpoints"]:
                yield endpoint_name

        for path, module_name, log_name, file_config in files():
            for rule_name, rule_config in rules(file_config):
                for transformation_name, transformation_config in transformations(rule_config):
                    for endpoint_name in endpoints(transformation_config):
                        yield path, module_name, log_name, rule_name, transformation_name, endpoint_name
