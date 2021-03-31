class FunctionNode:
    def __init__(self, child_nodes):
        self.child_nodes = child_nodes

    def calculate(self):
        return sum([node.calculate() for node in self.child_nodes])
