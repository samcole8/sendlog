from abc import ABC, ABCMeta

class SinkMeta(ABCMeta):
    pass

class Sink(ABC, metaclass=ABCMeta):
    pass
