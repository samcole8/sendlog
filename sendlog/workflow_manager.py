from importlib import import_module

from plugin import LogType, Rule, Transformer, Endpoint

from utils.errors import (EndpointVariableMismatchError,
                          PluginModuleNotFoundError,
                          PluginClassNotFoundError,
                          DestinationUndefinedError,
                          PluginInheritanceError)

PLUGIN_RPATHS = {
    "workflow": "plugins.workflows",
    "endpoint": "plugins.endpoints"
}

def resolve_class(parent, class_name):
    try:
        return getattr(parent, class_name)
    except AttributeError as e:
        raise PluginClassNotFoundError(class_name, parent) from e
        
def import_plugin(plugin_name, plugin_type="workflow"):
    try:
        return import_module(f"{PLUGIN_RPATHS[plugin_type]}.{plugin_name}")
    except ModuleNotFoundError as e:
        raise PluginModuleNotFoundError(plugin_name) from e

class WorkflowNode():
    """
    Wrapper for plugin classes.
    
    Stores plugin objects as part of a hierarchy and provides an unintrusive interface for accessing information about a plugin's origin.
    """

    def __init__(self, base_cls, node_obj):
        self._base_cls = base_cls
        self._node_obj = node_obj
        self._sub_nodes = []
        # Raise an error if the node object's class hasn't inherited from the specified base
        if self._base_cls not in self.node_bases():
            raise PluginInheritanceError(
                                            self.node_fullname(),
                                            self.base_fullname(),
                                            [
                                                f"{base.__module__}.{base.__qualname__}"
                                                for base in self.node_bases()
                                            ]
                                        )

    # Base information functions

    def base_cls(self):
        """Get the node's manually specified base class."""
        return self._base_cls

    def base_name(self):
        """Get the name of the node's manually specified base class."""
        return self._base_cls.__name__

    def base_fullname(self):
        """Get the full name of the node's manually specified base class."""
        return f"{self._base_cls.__module__}.{self._base_cls.__qualname__}"

    # Node information functions

    def node_class(self):
        """Get node class."""
        return self._node_obj.__class__

    def node_bases(self):
        """Get node class bases."""
        return self._node_obj.__class__.__bases__

    def node_name(self):
        """Get node class name."""
        return self._node_obj.__class__.__name__

    def node_fullname(self):
        """Get node class full name"""
        return f"{self._node_obj.__class__.__module__}.{self._node_obj.__class__.__qualname__}"

    # Other functions

    def execute(self, arg):
        """Execute a node object, assuming it is callable and takes one argument."""
        result = self._node_obj(arg)
        return result

    def __iter__(self):
        """Iterate through sub nodes."""
        return iter(self._sub_nodes)

    def add(self, sub_node):
        """Add a sub node."""
        self._sub_nodes.append(sub_node)
            

class WorkflowManager:
    def __init__(self):
        self._workflows = {}
        self._endpoints = {}

    def load_workflow(self, file_path: str, plugin_name: str, logtype_name: str, rule_name: str, transformer_name: str, endpoint_name: str):
        
        def _set_logtype(file_path, plugin_name, logtype_name):
            if file_path not in self._workflows.keys():
                plugin = import_plugin(plugin_name)
                LogTypePlugin = resolve_class(plugin, logtype_name)
                self._workflows[file_path] = WorkflowNode(LogType, LogTypePlugin())
            return self._workflows[file_path]

        def _set_rule(node, name):
            if not any(name == subnode.node_name() for subnode in node):
                node_obj = resolve_class(node.node_class(), name)()
                sub_node = WorkflowNode(Rule, node_obj)
                node.add(sub_node)
            else:
                sub_node = next((sub_node for sub_node in node if sub_node.node_name() == name), None)
            return sub_node

        def _set_transformer(node, name):
            if not any(name == subnode.node_name() for subnode in node):
                node_obj = resolve_class(node.node_class(), name)()
                sub_node = WorkflowNode(Transformer, node_obj)
                node.add(sub_node)
            else:
                sub_node = next((sub_node for sub_node in node if sub_node.node_name() == name), None)
            return sub_node
        
        def _set_endpoint(transformer_node, endpoint_name):
            # Extract Endpoint class and destination variables
            try:
                endpoint_data = self._endpoints[endpoint_name]
            except KeyError as e:
                raise DestinationUndefinedError(endpoint_name)
            endpoint_kwargs = endpoint_data["kwargs"] or {}
            ChannelPlugin = endpoint_data["channel"]
            sub_node = WorkflowNode(Endpoint, ChannelPlugin(endpoint_name, **endpoint_kwargs))
            transformer_node.add(sub_node)
            return sub_node

        logtype_node = _set_logtype(file_path, plugin_name, logtype_name)
        rule_node = _set_rule(logtype_node, rule_name)
        transformer_node = _set_transformer(rule_node, transformer_name)
        endpoint_node = _set_endpoint(transformer_node, endpoint_name)

        print(logtype_node.base_name(),":", logtype_node.node_name())
        print(rule_node.base_name(),":", rule_node.node_name())
        print(transformer_node.base_name(),":", transformer_node.node_name())
        print(endpoint_node.base_name(),":", endpoint_node.node_name())
        print()

    def load_endpoint(self, plugin_name: str, channel_name: str, endpoint_name: str, endpoint_kwargs: dict):
        plugin = import_plugin(plugin_name, plugin_type="endpoint")
        Channel = resolve_class(plugin, channel_name)
        self._endpoints[endpoint_name] = {"channel": Channel, "kwargs": endpoint_kwargs}
        if endpoint_kwargs is None:
            kws = set()
        else:
            kws = set(endpoint_kwargs.keys())
        if kws != set(Channel.required_vars):
            raise EndpointVariableMismatchError(endpoint_name, channel_name, set(Channel.required_vars), kws)

    def get_paths(self):
        return list(self._workflows.keys())

    def get_workflow(self, path):
        """Return a 'black-box' function that executes a workflow."""

        log_node = self._workflows[path]
        def workflow(log_line):
            for rule_node in log_node:
                if rule_node.execute(log_line) is True:
                    for transformer_node in rule_node:
                        msg = transformer_node.execute(log_line)
                        for endpoint_node in transformer_node:
                            endpoint_node.execute(msg)

        return workflow
