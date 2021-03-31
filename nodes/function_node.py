class FunctionNode:
    def __init__(self, child_nodes):
        self.child_nodes = child_nodes

    def calculate(self):
        return sum([node.calculate() for node in self.child_nodes])


if __name__ == '__main__':
    from terminal_node import TerminalNode
    testing_node = FunctionNode([TerminalNode(10)])
    print(testing_node.child_nodes)
    print(testing_node.calculate())
