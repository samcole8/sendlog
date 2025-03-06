from utils.errors import PluginOverrideError
import sys

class _WorkflowNode():
    
    """Base class for workflow components"""
    def __init__(self):
        self.children = []

    def _add_child(self, child_node):
        self.children.append(child_node)

    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__qualname__}"

    def __iter__(self):
        return iter(self.children)

# Metaclasses

class _NodeMeta(type):
    """Enforce elements for all plugins"""
    def __new__(cls, name, bases, dct):
        # Prevent `_execute` method from being overwritten if it is already defined
        if "_execute" in dct:
            if any("_execute" in base.__dict__ for base in bases):
                raise PluginOverrideError(name, "_execute")

        # Prevent node members from being overwritten
        restricted_members = ["__init__", "__repr__", "__iter__", "_add_child"]
        for member in restricted_members:
            if member in dct:
                raise PluginOverrideError(name, member)
        return super().__new__(cls, name, bases, dct)

class _TransformerMeta(_NodeMeta):
    """Enforce Transformers can only exist inside Rules"""
    def __new__(cls, name, bases, dct):
        
        return super().__new__(cls, name, bases, dct)

class _RuleMeta(_NodeMeta):
    """Enforce that rules can only exist inside LogTypes"""
    def __new__(cls, name, bases, dct):
        
        return super().__new__(cls, name, bases, dct)

class _LogTypeMeta(_NodeMeta):
    """Enforce that LogType is a base-level class."""
    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)

class _EndpointMeta(type):
    def __new__(cls, name, bases, dct):
        if "__init__" in dct:
            if any("__init__" in base.__dict__ for base in bases):
                raise PluginOverrideError(name, "__init__")
        if "__repr__" in dct:
            if any("__repr__" in base.__dict__ for base in bases):
                raise PluginOverrideError(name, "__repr__")
        return super().__new__(cls, name, bases, dct)

# Workflow classes

class Transformer(_WorkflowNode, metaclass=_TransformerMeta):
    def _execute(self, line):
        msg = self.transform(line)
        for endpoint in self.children:
            endpoint.send(msg)

    def transform(self, line):
        raise NotImplementedError

class Rule(_WorkflowNode, metaclass=_RuleMeta):
    def _execute(self, line):
        if self.evaluate(line) is True:
            for transformer in self.children:
                transformer._execute(line)
    
    def evaluate(self, line):
        raise NotImplementedError
    
    class Raw(Transformer):
        def transform(self, line):
            return line

class LogType(_WorkflowNode, metaclass=_LogTypeMeta):
    def _execute(self, line):
        for rule in self.children:
            rule._execute(line)
    
    class Always(Rule):
        def evaluate(self, line):
            return True

class Endpoint(metaclass=_EndpointMeta):
    required_vars = []
    def __init__(self, name, **kwargs):
        self.name = name

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__qualname__} <- {self.name}"

    def send(self, msg):
        raise NotImplementedError

__all__ = ["LogType", "Rule", "Transformer", "Endpoint"]
