from sendlog.base import Base, BaseMeta

class SourceMeta(BaseMeta):
    pass

class Source(Base, metaclass=SourceMeta):
    __slots__ = []
    