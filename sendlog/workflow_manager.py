from importlib import import_module

FILE_PLUGIN_RPATH = "plugins.workflows"
ENDPOINT_PLUGIN_RPATH = "plugins.endpoints"

def resolve_class(parent, class_name):
    return getattr(parent, class_name)
        
def import_plugin(plugin):
    return import_module(plugin)

class WorkflowManager:
    def __init__(self):
        self._workflows = {}
        self._destinations = {}

    def load_workflow(self, file_path, plugin_name, logtype_name, rule_name, transformer_name, destination_name):
        """Load a workflow based on the given parameters."""

        # Set or load Log object
        if file_path not in self._workflows.keys():
            current_plugin = import_plugin(FILE_PLUGIN_RPATH + "." + plugin_name)
            current_log = resolve_class(current_plugin, logtype_name)
            logtype_node = current_log()
            self._workflows[file_path] = logtype_node
        else:
            logtype_node = self._workflows[file_path]

        # Set or load Rule objects
        full_rule_name = repr(logtype_node) + "." + rule_name
        if full_rule_name not in logtype_node:
            current_rule = resolve_class(logtype_node, rule_name)
            rule_node = current_rule()
            logtype_node.add_child(rule_node)
        else:
            rule_node = next((child for child in logtype_node.children if repr(child) == full_rule_name), None)

        # Set or load transformer objects
        full_transformer_name = repr(rule_node) + "." + transformer_name
        if full_transformer_name not in rule_node:
            current_transformer = resolve_class(rule_node, transformer_name)
            transformer_node = current_transformer()
            rule_node.add_child(transformer_node)
        else:
            transformer_node = next((child for child in rule_node.children if repr(child) == full_transformer_name), None)
            
        # Set or load Destinations
        destination_class = self._destinations[destination_name]["class"]
        transformer_node.add_child(destination_class(destination_name, self._destinations[destination_name]["class"].__name__, **self._destinations[destination_name]["vars"]))

    def load_destinations(self, plugin_name, endpoint_name, destination_name, destination_vars):
        endpoint_plugin = import_plugin(f"{ENDPOINT_PLUGIN_RPATH}.{plugin_name}")
        endpoint_class = resolve_class(endpoint_plugin, endpoint_name)
        self._destinations[destination_name] = {"class": endpoint_class,
                                      "vars": destination_vars}

    def get_paths(self):
        return list(self._workflows.keys())

    def get_workflow(self, path):
        return self._workflows[path]
