class _WorkflowNode:
    
    """Base class for workflow components"""
    def __init__(self, level):
        self.level = level
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__qualname__}"

    def __iter__(self):
        return iter(self.children)