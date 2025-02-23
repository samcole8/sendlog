from importlib import import_module
import endpoints

PLUGIN_RPATH = "plugins"

def resolve_class(parent, class_name):
    return getattr(parent, class_name)
        
def import_plugin(plugin):
    return import_module(plugin)

class WorkflowManager:
    def __init__(self):
        self._workflows = {}
        self._cache = {}

    def load_workflow(self, path, plugin_name, log_name, rule_name, transformation_name, endpoint_name):
        """Load a workflow based on the given parameters."""

        # Set or load Log object
        if path not in self._workflows.keys():
            current_plugin = import_plugin(PLUGIN_RPATH + "." + plugin_name)
            current_log = resolve_class(current_plugin, log_name)
            log_node = current_log("format")
            self._workflows[path] = log_node
        else:
            log_node = self._workflows[path]

        # Set or load Rule objects
        full_rule_name = repr(log_node) + rule_name
        
        if full_rule_name not in log_node.children:
            current_rule = resolve_class(log_node, rule_name)
            rule_node = current_rule("rule")
            log_node.add_child(rule_node)
        else:
            rule_node = next((child for child in log_node.children if repr(child) == full_rule_name), None)
            print(rule_node)
        # Set or load Transformation objects
        full_transformation_name = repr(rule_node) + transformation_name
        
        if full_transformation_name not in rule_node.children:
            current_transformation = resolve_class(rule_node, transformation_name)
            transformation_node = current_transformation("transformation")
            rule_node.add_child(transformation_node)
        else:
            transformation_node = next((child for child in rule_node.children if repr(child) == full_transformation_name), None)
            
        
        # Set or load Endpoints
        full_endpoint_name = f"endpoints.{endpoint_name}"
        if full_endpoint_name not in transformation_node.children:
            current_endpoint = resolve_class(endpoints, endpoint_name)
            endpoint_node = current_endpoint("endpoint")
            transformation_node.add_child(endpoint_name)
        else:
            endpoint_node = next((child for child in transformation_node.children if repr(child) == endpoint_name), None)

    def get_paths(self):
        return list(self._workflows.keys())

    def get_workflow(self, path):
        return self._workflows[path]
