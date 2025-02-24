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

class _LogMeta(type):
    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)

class _RuleMeta(type):
    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)

class _TransformationMeta(type):
    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)

class _EndpointMeta(type):
    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)

class Log(_WorkflowNode, metaclass=_LogMeta):
    def execute(self, line):
        for rule in self.children:
            rule.execute(line)

class Rule(_WorkflowNode, metaclass=_RuleMeta):
    def execute(self, line):
        if self.evaluate(line) is True:
            for transformation in self.children:
                transformation.execute(line)
    
    def evaluate(self, line):
        raise NotImplementedError

class Transformation(_WorkflowNode, metaclass=_TransformationMeta):
    def execute(self, line):
        msg = self.transform(line)
        for endpoint in self.children:
            endpoint.send(msg)

    def transform(self, line):
        raise NotImplementedError

class Endpoint(metaclass=_EndpointMeta):
    def __init__(self, dest_name, **kwargs):
        self.dest_name = dest_name
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"{self.__class__.__name__} ({self.dest_name})"

    def send(self, msg):
        raise NotImplementedError

__all__ = ["Log", "Rule", "Transformation", "Endpoint"]
