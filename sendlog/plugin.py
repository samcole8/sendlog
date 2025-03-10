from utils.errors import PluginOverrideError, PluginInitError
import sys

# Metaclasses

class _NodeMeta(type):
    """Enforce elements for all plugins"""
    def __new__(cls, name, bases, dct):
        # Prevent parameters other than self in __init__ methods
        if "__init__" in dct:
            init_method = dct["__init__"]
            init_params = init_method.__code__.co_varnames[1:]
            if init_params:
                raise PluginInitError(name, init_method.__code__.co_varnames)
        return super().__new__(cls, name, bases, dct)

class _TransformerMeta(_NodeMeta):
    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)

class _RuleMeta(_NodeMeta):
    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)

class _LogTypeMeta(_NodeMeta):
    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)

class _EndpointMeta(type):
    def __new__(cls, name, bases, dct):
        if "__init__" in dct:
            if any("__init__" in base.__dict__ for base in bases):
                raise PluginOverrideError(name, "__init__")
        return super().__new__(cls, name, bases, dct)

# Workflow classes

class Transformer(metaclass=_TransformerMeta):

    def __call__(self, line):
        raise NotImplementedError

class Rule(metaclass=_RuleMeta):
    
    def __call__(self, line):
        raise NotImplementedError
    
    class Raw(Transformer):
        def __call__(self, line):
            return line

class LogType(metaclass=_LogTypeMeta):
    
    class Always(Rule):
        def __call__(self, line):
            return True

class Endpoint(metaclass=_EndpointMeta):
    required_vars = []
    def __init__(self, name, **kwargs):
        self.name = name

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __call__(self, msg):
        raise NotImplementedError

__all__ = ["LogType", "Rule", "Transformer", "Endpoint"]
