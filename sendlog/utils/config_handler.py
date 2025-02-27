from importlib import import_module
import yaml

class ConfigHandler:
    """Initialises and stores objects referenced in the configuration file."""
    def __init__(self, path):
        self._path = path
        self._config = {}
        self.load_config()

    def load_config(self):
        with open(self._path, "r") as file:
            self._config = yaml.safe_load(file)

    def files(self):
        """
        Traverse the configuration file and yield information about every alert in the following format:

        (path, module_name, log_name, rule_name, transformer_name, dest_name)
        """
        
        def files():
            for path, file_config in self._config["files"].items():
                yield path, file_config["plugin"], file_config["log_type"], file_config
        
        def rules(file_config):
            for rule_name, rule_config in file_config["rules"].items():
                yield rule_name, rule_config
        
        def transformers(rule_config):
            for transformer_name, transformer_config in rule_config["transformers"].items():
                yield transformer_name, transformer_config
        
        def destinations(transformer_config):
            for destination_name in transformer_config["destinations"]:
                yield destination_name

        for path, plugin_name, log_name, file_config in files():
            for rule_name, rule_config in rules(file_config):
                for transformer_name, transformer_config in transformers(rule_config):
                    for destination_name in destinations(transformer_config):
                        yield path, plugin_name, log_name, rule_name, transformer_name, destination_name

    def destinations(self):
        for dest_name, dest_config in self._config["destinations"].items():
            plugin_name = dest_config["plugin"]
            endpoint_name = dest_config["endpoint"]
            dest_vars = dest_config.get("vars", None)
            yield plugin_name, endpoint_name, dest_name, dest_vars
