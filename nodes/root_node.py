from function_node import FunctionNode
from terminal_node import TerminalNode


class RootNode(FunctionNode):
    """Calculates the amount to invest or sell"""

    def __init__(self, child_nodes):
        super().__init__(child_nodes)
        self.purchasing_power = 1000
    
    def get_decision(self):
        return self.calculate()
