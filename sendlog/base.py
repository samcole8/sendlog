from abc import ABC, ABCMeta

class BaseMeta(ABCMeta):
    pass

class Base(ABC, metaclass=BaseMeta):
    __slots__ = []
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key not in self.__slots__:
                raise TypeError(f"Unknown parameter: {key}")
            setattr(self, key, value)