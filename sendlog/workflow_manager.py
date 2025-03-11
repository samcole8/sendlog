from importlib import import_module

from plugin import LogType, Rule, Transformer, Channel
from utils import clsi
from utils.errors import (EndpointVariableMismatchError,
                          PluginModuleNotFoundError,
                          PluginClassNotFoundError,
                          DestinationUndefinedError,
                          PluginInheritanceError)

PLUGIN_RPATHS = {
    "log": "plugins.logs",
    "channel": "plugins.channels"
}

def resolve_class(parent, class_name):
    try:
        return getattr(parent, class_name)
    except AttributeError as e:
        raise PluginClassNotFoundError(class_name, parent) from e
        
def import_plugin(plugin_name, plugin_type="log"):
    try:
        return import_module(f"{PLUGIN_RPATHS[plugin_type]}.{plugin_name}")
    except ModuleNotFoundError as e:
        raise PluginModuleNotFoundError(plugin_name) from e

class WorkflowNode():
    """
    Wrapper for plugin classes.
    
    Store plugin objects as part of a hierarchy.
    """

    def __init__(self, base_cls, node_obj):
        self._base_cls = base_cls
        self._node_obj = node_obj
        self._sub_nodes = []
        # Raise an error if the node object's class hasn't inherited from the specified base
        if self._base_cls not in clsi.obj_bases(self._node_obj):
            raise PluginInheritanceError(
                                            clsi.obj_fullname(self._node_obj),
                                            clsi.cls_fullname(self._base_cls),
                                            [
                                                clsi.cls_fullname(base)
                                                for base in clsi.cls_bases(self._base_cls)
                                            ]
                                        )

    @property
    def obj(self):
        return self._node_obj
    
    @property
    def base(self):
        return self._base_cls

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
                print(f"Loaded workflows for file: {file_path}\n")
                plugin = import_plugin(plugin_name)
                LogTypePlugin = resolve_class(plugin, logtype_name)
                self._workflows[file_path] = WorkflowNode(LogType, LogTypePlugin())
            return self._workflows[file_path]

        def _set_rule(node, name):
            # If rule node is not in logtype node
            if not any(name == clsi.obj_name(subnode.obj) for subnode in node):
                rule_obj = resolve_class(clsi.obj_class(node.obj), name)()
                sub_node = WorkflowNode(Rule, rule_obj)
                node.add(sub_node)
            else:
                # Use existing rule node
                sub_node = next((sub_node for sub_node in node if clsi.obj_name(sub_node.obj) == name), None)
            return sub_node

        def _set_transformer(node, name):
            # If transformer node is not in rule node
            if not any(name == clsi.obj_name(subnode.obj) for subnode in node):
                transformer_obj = resolve_class(clsi.obj_class(node.obj), name)()
                sub_node = WorkflowNode(Transformer, transformer_obj)
                node.add(sub_node)
            else:
                # Use existing transformer node
                sub_node = next((sub_node for sub_node in node if clsi.obj_name(sub_node.obj) == name), None)
            return sub_node
        
        def _set_endpoint(transformer_node, endpoint_name):
            # Extract Channel class and endpoint variables
            try:
                endpoint_data = self._endpoints[endpoint_name]
            except KeyError as e:
                raise DestinationUndefinedError(endpoint_name)
            endpoint_kwargs = endpoint_data["kwargs"] or {}
            ChannelPlugin = endpoint_data["channel"]
            try:
                channel_obj = ChannelPlugin(endpoint_name, **endpoint_kwargs)
            except TypeError:
                raise PluginInheritanceError(clsi.cls_name(ChannelPlugin), clsi.cls_name(Channel) ,clsi.cls_bases(ChannelPlugin))
            sub_node = WorkflowNode(Channel, channel_obj)

            transformer_node.add(sub_node)
            return sub_node

        logtype_node = _set_logtype(file_path, plugin_name, logtype_name)
        rule_node = _set_rule(logtype_node, rule_name)
        transformer_node = _set_transformer(rule_node, transformer_name)
        endpoint_node = _set_endpoint(transformer_node, endpoint_name)

        print(clsi.cls_name(logtype_node.base),":", clsi.obj_name(logtype_node.obj))
        print(clsi.cls_name(rule_node.base),":", clsi.obj_name(rule_node.obj))
        print(clsi.cls_name(transformer_node.base),":", clsi.obj_name(transformer_node.obj))
        print(clsi.cls_name(endpoint_node.base),":", clsi.obj_name(endpoint_node.obj), " -> ", endpoint_node.obj.name)
        print()

    def load_endpoint(self, plugin_name: str, channel_name: str, endpoint_name: str, endpoint_kwargs: dict):
        plugin = import_plugin(plugin_name, plugin_type="channel")
        ChannelPlugin = resolve_class(plugin, channel_name)

        self._endpoints[endpoint_name] = {"channel": ChannelPlugin, "kwargs": endpoint_kwargs}
        if endpoint_kwargs is None:
            kws = set()
        else:
            kws = set(endpoint_kwargs.keys())
        if kws != set(ChannelPlugin.required_vars):
            raise EndpointVariableMismatchError(endpoint_name, channel_name, set(ChannelPlugin.required_vars), kws)

    def get_paths(self):
        return list(self._workflows.keys())

    def display_nodes(self):
        for key, node in self._workflows.items():
            print(key)
            print(clsi.obj_fullname(node.obj))
            for subnode in node:
                print(" ", clsi.obj_fullname(subnode.obj))
                for subnode in subnode:
                    print("   ", clsi.obj_fullname(subnode.obj))
                    for subnode in subnode:
                        print("     ", clsi.obj_fullname(subnode.obj), "->", subnode.obj.name)
            print()

    def get_workflow(self, path):
        """Return a 'black-box' function that executes a workflow."""

        log_node = self._workflows[path]
        def workflow(log_line):
            for rule_node in log_node:
                if rule_node.obj(log_line) is True:
                    for transformer_node in rule_node:
                        msg = transformer_node.obj(log_line)
                        for endpoint_node in transformer_node:
                            endpoint_node.obj(msg)

        return workflow
