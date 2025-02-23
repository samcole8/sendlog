from plugin import _WorkflowNode

class Console(_WorkflowNode):

    def send(self, msg):
        print(msg)