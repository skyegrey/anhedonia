from nodes.function_node import FunctionNode


class RootNode(FunctionNode):
    """Calculates the amount to invest or sell"""

    def __init__(self, child_nodes):
        super().__init__(child_nodes)
        self.purchasing_power = 20
        self.asset_count = 0
        self.max_arity = 10
    
    def get_decision(self, frame_data):
        return self.calculate(frame_data)
