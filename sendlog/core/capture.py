from .transformer import Transformer, TransformerMeta

class CaptureMeta(TransformerMeta):
    pass

class Capture(Transformer, metaclass=CaptureMeta):
    logic = all # all or any
