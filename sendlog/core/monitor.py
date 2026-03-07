from abc import ABC, ABCMeta

class MonitorMeta(ABCMeta):
    pass

class Monitor(ABC, metaclass=MonitorMeta):
    source = None
    flows = None
