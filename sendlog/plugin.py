from utils.errors import PluginOverrideError, PluginInitError
from abc import ABC, ABCMeta, abstractmethod
import sys
import re

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

    def __call__(self, log_parts):
        return log_parts["message"]

class Rule(ABC, metaclass=_RuleMeta):

    regex = None
    
    def __call__(self, log_parts):
        """Convert log message to structured JSON."""
        if self.__class__.regex:
            match = re.match(self.__class__.regex, log_parts["message"])
            if match:
                message_parts = match.groupdict()
                return {**log_parts, "context": {**message_parts}}
        return False

class LogType(ABC, metaclass=_LogTypeMeta):
    """
    Base class for a LogType plugin.
    """

    regex = None

    def __call__(self, log_line):
        """
        Convert log_line to structured JSON using regex.
        
        Must return a dictionary with the "message" key.
        """
        if self.__class__.regex:
            match = re.match(self.__class__.regex, log_line)
            if match:
                log_parts = match.groupdict()
                return log_parts
            else:
                raise TypeError("Log line did not match the expected format.")
        else:
            return {"message": log_line}

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
