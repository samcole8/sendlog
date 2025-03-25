from utils.errors import PluginOverrideError, PluginInitError
from abc import ABC, ABCMeta, abstractmethod
import sys

# Metaclasses

class _NodeMeta(ABCMeta):
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

class _ChannelMeta(ABCMeta):
    def __new__(cls, name, bases, dct):
        if "__init__" in dct:
            if any("__init__" in base.__dict__ for base in bases):
                raise PluginOverrideError(name, "__init__")
        return super().__new__(cls, name, bases, dct)

# Workflow classes

class Transformer(ABC, metaclass=_TransformerMeta):

    def __call__(self, log_line):
        return log_line

class Rule(ABC, metaclass=_RuleMeta):
    
    def __call__(self, log_line):
        return True

class LogType(ABC, metaclass=_LogTypeMeta):

    def __call__(self, log_line):
        return log_line

class Channel(ABC, metaclass=_ChannelMeta):
    required_vars = []
    def __init__(self, name, **kwargs):
        self.name = name

        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def __call__(self, msg):
        pass

__all__ = ["LogType", "Rule", "Transformer", "Channel"]
