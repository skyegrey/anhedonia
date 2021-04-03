class TerminalNode:
    def __init__(self, terminal_type, terminal_value):
        self.type = terminal_type
        self.terminal_value = terminal_value

    def calculate(self, frame_data):
        return self.terminal_value if self.type == 'constant' else \
            frame_data[self.terminal_value.frame][self.terminal_value.key]
