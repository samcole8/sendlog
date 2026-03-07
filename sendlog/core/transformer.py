from abc import ABC, ABCMeta

class TransformerMeta(ABCMeta):
    def __or__(cls, sink):
        return None


class Transformer(ABC, metaclass=TransformerMeta):
    pass