from abc import ABC, abstractmethod
from importlib import import_module

from plugin import LogType, Rule, Transformer, Channel
from utils import clsi
from utils.errors import (EndpointVariableMismatchError,
                          PluginModuleNotFoundError,
                          PluginClassNotFoundError,
                          DestinationUndefinedError,
                          PluginInheritanceError)

PLUGIN_HIERARCHY = {0: LogType,
                    1: Rule,
                    2: Transformer,
                    3: Channel}

def resolve_class(parent, class_name):
    try:
        return getattr(parent, class_name)
    except AttributeError as e:
        raise PluginClassNotFoundError(class_name, parent)
        
def import_plugin(plugin_name, plugin_type):
    try:
        return import_module(f"plugins.{plugin_type}.{plugin_name}")
    except ModuleNotFoundError as e:
        raise PluginModuleNotFoundError(plugin_name)

class WorkflowNode(ABC):
    """
    Wrapper for plugin classes.
    
    Store plugin objects as part of a hierarchy.
    """

    @abstractmethod
    def __init__(self, level, plugin_cls):
        self._level = level
        self._plugin_cls = plugin_cls
        self._subnodes = []
        # Validate plugin class
        if self.base_cls not in self.plugin_cls.__bases__:
            raise PluginInheritanceError(self.plugin_cls.__name__, self.base_cls.__name__, [base.__name__ for base in self.plugin_cls.__bases__])
        # Instantiate plugin class
        self._inst_plugin()

    @property
    def plugin_cls(self):
        return self._plugin_cls

    @property
    def plugin_obj(self):
        return self._plugin_obj

    @property
    def base_cls(self):
        return PLUGIN_HIERARCHY[self._level]

    def __iter__(self):
        """Iterate through sub nodes."""
        return iter(self._subnodes)
    
    def _inst_plugin(self):
        self._plugin_obj = self._plugin_cls()

    def add(self, subnode):
        # Validate subnode inherits from the correct plugin class
        if PLUGIN_HIERARCHY[self._level + 1] not in subnode.plugin_cls.__bases__:
            raise PluginInheritanceError(self.plugin_cls.__name__, self.base_cls.__name__, [base.__name__ for base in subnode.plugin_cls.__bases__])
        # Add subnode to node
        self._subnodes.append(subnode)

class LogTypeNode(WorkflowNode):

    def __init__(self, plugin_cls):
        self._level = 0
        super().__init__(self._level, plugin_cls)

class RuleNode(WorkflowNode):

    def __init__(self, plugin_cls):
        self._level = 1
        super().__init__(self._level, plugin_cls)

class TransformerNode(WorkflowNode):

    def __init__(self, plugin_cls):
        self._level = 2
        super().__init__(self._level, plugin_cls)

class EndpointNode(WorkflowNode):

    def __init__(self, channel_cls, endpoint_kwargs, endpoint_name):
        self._level = 3
        self._endpoint_kwargs = endpoint_kwargs
        self.endpoint_name = endpoint_name
        super().__init__(self._level, channel_cls)

    def _inst_plugin(self):
        self._plugin_obj = self._plugin_cls(self.endpoint_name, **self._endpoint_kwargs)

class WorkflowManager():
    """Load, store and orchestrate workflow executions."""
    
    def __init__(self):
        self._files = {}
        self._endpoints = {}
    
    def load_file(self, file_path: str, plugin_name: str, logtype_name: str, rule_name: str, transformer_name: str, endpoint_name: str):
        """Idempotently load a workflow from the reference strings provided."""

        def get_subnode(node, plugin_cls):
            rule_node = next((subnode for subnode in node if subnode.plugin_obj.__class__ == plugin_cls), None)
            return rule_node
        
        # Get/set LogType node
        logtype_node = self._files.get(file_path)
        if logtype_node is None:
            plugin_mod = import_plugin(plugin_name, "logs")
            logtype_cls = resolve_class(plugin_mod, logtype_name)
            logtype_node = LogTypeNode(logtype_cls)
            self._files[file_path] = logtype_node
        else:
            logtype_cls = logtype_node.plugin_obj.__class__

        # Get/set Rule node
        rule_cls = resolve_class(logtype_cls, rule_name)
        rule_node = get_subnode(logtype_node, rule_cls)
        if rule_node is None:
            rule_node = RuleNode(rule_cls)
            logtype_node.add(rule_node)

        # Get/set Transformer node
        transformer_cls = resolve_class(rule_cls, transformer_name)
        transformer_node = get_subnode(rule_node, transformer_cls)
        if transformer_node is None:
            transformer_node = TransformerNode(transformer_cls)
            rule_node.add(transformer_node)
        
        # Set endpoint node
        try:
            endpoint_data = self._endpoints[endpoint_name]
        except KeyError:
            raise DestinationUndefinedError(endpoint_name)
        channel_cls = endpoint_data["channel_cls"]
        endpoint_kwargs = endpoint_data["kwargs"]
        endpoint_node = EndpointNode(channel_cls, endpoint_kwargs, endpoint_name)
        transformer_node.add(endpoint_node)

        # Display workflow
        print("WORKFLOW LOADED:\n")
        print("File", ":", file_path)
        print("LogType",":", clsi.obj_name(logtype_node.plugin_obj))
        print("Rule",":", clsi.obj_name(rule_node.plugin_obj))
        print("Transformer", ":", clsi.obj_name(transformer_node.plugin_obj))
        print("Channel",":", clsi.obj_name(endpoint_node.plugin_obj), f"({endpoint_node.endpoint_name})")
        print()

    def load_endpoint(self, plugin_name: str, channel_name: str, endpoint_name: str, endpoint_kwargs: dict):
        # Resolve channel class
        plugin_mod = import_plugin(plugin_name, "channels")
        channel_cls = resolve_class(plugin_mod, channel_name)
        # Validate that endpoint keyword arguments match the specified channel
        given_kws = set(endpoint_kwargs.keys())
        required_kws = set(channel_cls.required_vars)
        if given_kws != required_kws:
            raise EndpointVariableMismatchError(endpoint_name, channel_name, required_kws, given_kws)
        # Store channel class and arguments for later
        self._endpoints[endpoint_name] = {"channel_cls": channel_cls, "kwargs": endpoint_kwargs}

    def get_workflow(self, path):
        """Return a 'black-box' function that executes a workflow."""

        log_node = self._files[path]

        def workflow(log_line):
            """Execute a workflow and raise errors related to its execution."""
            for rule_node in log_node:
                if rule_node.plugin_obj(log_line) is True:
                    for transformer_node in rule_node:
                        msg = transformer_node.plugin_obj(log_line)
                        for endpoint_node in transformer_node:
                            endpoint_node.plugin_obj(msg)
        return workflow
    
    def get_paths(self):
        return list(self._files.keys())
    
    def display_worktrees(self):
        """Traverse nodes and display the worktree with tree-like notation."""

        def display_subnodes(node, prefix=""):
            subnodes = list(node)
            # Display list subnodes
            for i, subnode in enumerate(subnodes):
                connector = "└──" if i == len(subnodes) - 1 else "├──"
                msg = prefix + connector + " " + subnode.plugin_cls.__name__
                if subnode.__class__ is EndpointNode:
                    msg += f" ({subnode.endpoint_name})"
                print(msg)

                # Recurse if there are subnodes
                if any(subnode):
                    display_subnodes(subnode, prefix + ("    " if i == len(subnodes) - 1 else "│   "))

        print(f"{len(self._files)} ACTIVE WORKTREES:\n")

        for path, node in self._files.items():
            print(path)
            print(node.plugin_cls.__name__)
            display_subnodes(node)
            print()
