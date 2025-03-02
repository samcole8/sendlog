from importlib import import_module

from utils.errors import EndpointVariableMismatchError

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

        def _set_logtype(file_path, plugin_name, logtype_name):
            if file_path not in self._workflows.keys():
                current_plugin = import_plugin(FILE_PLUGIN_RPATH + "." + plugin_name)
                current_log = resolve_class(current_plugin, logtype_name)
                logtype_node = current_log()
                self._workflows[file_path] = logtype_node
            return self._workflows[file_path]
            
        def _set_rule(logtype_node, rule_name):
            full_rule_name = repr(logtype_node) + "." + rule_name
            if full_rule_name not in logtype_node:
                current_rule = resolve_class(logtype_node, rule_name)
                rule_node = current_rule()
                logtype_node.add_child(rule_node)
            else:
                rule_node = next((child for child in logtype_node.children if repr(child) == full_rule_name), None)
            return rule_node

        def _set_destination(transformer_node, destination_name):
            # Set or load Destinations
            destination_class = self._destinations[destination_name]["class"]
            destination_vars = self._destinations[destination_name]["vars"] or {}
            destination_node = destination_class(destination_name, **destination_vars)
            transformer_node.add_child(destination_node)
            return destination_node
        
        logtype_node = _set_logtype(file_path, plugin_name, logtype_name)
        rule_node = _set_rule(logtype_node, rule_name)
        transformer_node = _set_rule(rule_node, transformer_name) # Set transformer
        destination_node = _set_destination(transformer_node, destination_name)

        #print(f"\n{file_path}:\n{logtype_node}\n{rule_node}\n{transformer_node}\n{destination_node}")

    def load_destinations(self, plugin_name, endpoint_name, destination_name, destination_vars):
        endpoint_plugin = import_plugin(f"{ENDPOINT_PLUGIN_RPATH}.{plugin_name}")
        endpoint_class = resolve_class(endpoint_plugin, endpoint_name)
        self._destinations[destination_name] = {"class": endpoint_class, "vars": destination_vars}
        if set(endpoint_class.required_vars) != set(destination_vars.keys()):
            raise EndpointVariableMismatchError(destination_name, endpoint_name, set(endpoint_class.required_vars), set(destination_vars.keys()))
    
    def get_paths(self):
        return list(self._workflows.keys())

    def get_workflow(self, path):
        return self._workflows[path]
