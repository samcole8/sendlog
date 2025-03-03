from utils.errors import ConfigurationKeyError, ConfigurationTypeError

from importlib import import_module
import yaml

def get_val(key, dicti, enforced_type=None):
    try:
        val = dicti[key]
    except (KeyError, TypeError) as e:
        raise ConfigurationKeyError(key) from e

    if enforced_type != None:
        if type(val) is not enforced_type:
            raise ConfigurationTypeError(enforced_type.__name__, type(val).__name__)
    return dicti[key]

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
            for path, file_config in get_val("files", self._config, dict).items():
                yield path, get_val("plugin", file_config, str), get_val("log_type", file_config, str), file_config
        
        def rules(file_config):
            for rule_name, rule_config in get_val("rules", file_config, dict).items():
                yield rule_name, rule_config
        
        def transformers(rule_config):
            for transformer_name, transformer_config in get_val("transformers", rule_config, dict).items():
                yield transformer_name, transformer_config
        
        def destinations(transformer_config):
            for destination_name in get_val("destinations", transformer_config, list):
                yield destination_name

        for path, plugin_name, log_name, file_config in files():
            for rule_name, rule_config in rules(file_config):
                for transformer_name, transformer_config in transformers(rule_config):
                    for destination_name in destinations(transformer_config):
                        for item in path, plugin_name, log_name, rule_name, transformer_name, destination_name:
                            if type(item) is not str:
                                raise ConfigurationTypeError("str", type(item).__name__)
                        yield path, plugin_name, log_name, rule_name, transformer_name, destination_name

    def destinations(self):
        for dest_name, dest_config in get_val("destinations", self._config, dict).items():
            plugin_name = get_val("plugin", dest_config, str)
            endpoint_name =  get_val("endpoint", dest_config, str)
            dest_vars = dest_config.get("vars", None)
            yield plugin_name, endpoint_name, dest_name, dest_vars
