class FunctionNode:
    def __init__(self, child_nodes):
        self.child_nodes = child_nodes

    def calculate(self, frame_data):
        return sum([node.calculate(frame_data) for node in self.child_nodes])
