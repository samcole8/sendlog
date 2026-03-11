from sendlog.base import Base, BaseMeta

class SinkMeta(BaseMeta):
    pass

class Sink(Base, metaclass=SinkMeta):
    __slots__ = []
