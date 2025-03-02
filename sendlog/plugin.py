class _WorkflowNode:
    
    """Base class for workflow components"""
    def __init__(self):
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__qualname__}"

    def __iter__(self):
        return iter(self.children)

# Metaclasses

class _TransformerMeta(type):
    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)

class _RuleMeta(type):
    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)

class _LogTypeMeta(type):
    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)

class _EndpointMeta(type):
    def __new__(cls, name, bases, dct):
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

class LogType(_WorkflowNode, metaclass=_LogTypeMeta):
    def _execute(self, line):
        for rule in self.children:
            rule._execute(line)

class Endpoint(metaclass=_EndpointMeta):
    required_vars = []
    def __init__(self, dest_name, **kwargs):
        self.dest_name = dest_name

        # Assign variables and validate
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__qualname__} ({self.dest_name})"

    def send(self, msg):
        raise NotImplementedError

__all__ = ["LogType", "Rule", "Transformer", "Endpoint"]
