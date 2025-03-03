from importlib import import_module

from utils.errors import EndpointVariableMismatchError, PluginModuleNotFoundError, PluginClassNotFoundError, DestinationUndefinedError

FILE_PLUGIN_RPATH = "plugins.workflows"
ENDPOINT_PLUGIN_RPATH = "plugins.endpoints"

def resolve_class(parent, class_name):
    try:
        return getattr(parent, class_name)
    except AttributeError as e:
        raise PluginClassNotFoundError(class_name, parent) from e
        
def import_plugin(plugin):
    try:
        return import_module(plugin)
    except ModuleNotFoundError as e:
        raise PluginModuleNotFoundError(plugin) from e

class WorkflowManager:
    def __init__(self):
        self._workflows = {}
        self._destinations = {}

    def load_workflow(self, file_path, plugin_name, logtype_name, rule_name, transformer_name, destination_name):
        """Idempotently load elements of a workflow based on the given parameters."""
        def _set_logtype(file_path, plugin_name, logtype_name):
            """Idempotently load a LogType."""
            if file_path not in self._workflows.keys():
                # Import plugin
                plugin = import_plugin(f"{FILE_PLUGIN_RPATH}.{plugin_name}")
                # Resolve and instantiate LogType object
                LogType = resolve_class(plugin, logtype_name)
                self._workflows[file_path] = LogType()
            return self._workflows[file_path]
            
        def _set_rule(logtype_node, rule_name):
            """Idempotently load a Rule or Transformer."""
            rule_id = f"{logtype_node}.{rule_name}"
            if rule_id not in logtype_node:
                Rule = resolve_class(logtype_node, rule_name)
                rule_node = Rule()
                logtype_node.add_child(rule_node)
            else:
                rule_node = next((child for child in logtype_node.children if child == rule_id), None)
            return rule_node

        def _set_destination(transformer_node, destination_name):
            """Load an Endpoint."""
            # Extract Endpoint class and destination variables
            try:
                Endpoint = self._destinations[destination_name]["class"]
            except KeyError as e:
                raise DestinationUndefinedError(destination_name) from e
            destination_vars = self._destinations[destination_name]["vars"] or {}
            # Instantiate the destination object
            destination_node = Endpoint(destination_name, **destination_vars)
            transformer_node.add_child(destination_node)
            return destination_node

        logtype_node = _set_logtype(file_path, plugin_name, logtype_name)
        rule_node = _set_rule(logtype_node, rule_name)
        transformer_node = _set_rule(rule_node, transformer_name) # Set transformer
        destination_node = _set_destination(transformer_node, destination_name)

        #print(f"\n\nReceived {file_path}, {plugin_name}, {logtype_name}, {rule_name}, {transformer_name}, {destination_name}")
        #print(f"\nWorkflow loaded:\n  Path:        {file_path}\n  LogType:     {logtype_node}\n  Rule:        {rule_node}\n  Transformer: {transformer_node}\n  Destination: {destination_node}")

    def load_destinations(self, plugin_name, endpoint_name, destination_name, destination_vars):
        endpoint_plugin = import_plugin(f"{ENDPOINT_PLUGIN_RPATH}.{plugin_name}")
        endpoint_class = resolve_class(endpoint_plugin, endpoint_name)
        self._destinations[destination_name] = {"class": endpoint_class, "vars": destination_vars}
        if destination_vars is None:
            destination_vars = {None:None}
        if set(endpoint_class.required_vars) != set(destination_vars.keys()):
            raise EndpointVariableMismatchError(destination_name, endpoint_name, set(endpoint_class.required_vars), set(destination_vars.keys()))
    
    def get_paths(self):
        return list(self._workflows.keys())

    def get_workflow(self, path):
        return self._workflows[path]
