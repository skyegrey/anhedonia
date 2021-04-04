class FunctionNode:
    def __init__(self, function_data, child_nodes):
        self.function_data = function_data
        self.child_nodes = child_nodes

    def calculate(self, frame_data, root_statistics):
        return self.function_data.function([node.calculate(frame_data, root_statistics) for node in self.child_nodes])
