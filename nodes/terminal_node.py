class TerminalNode:
    def __init__(self, value):
        self.value = value

    def calculate(self):
        return self.value


if __name__ == '__main__':
    testing_node = TerminalNode(5)
    print(testing_node.calculate())
