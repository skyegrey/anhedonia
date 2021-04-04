class TerminalNode:
    def __init__(self, terminal_type, terminal_value):
        self.type = terminal_type
        self.terminal_value = terminal_value

    def calculate(self, frame_data, root_statistics):
        calculated_value = None
        if self.type == 'constant':
            calculated_value = self.terminal_value
        elif self.type == 'run_time_evaluated':
            calculated_value = frame_data[self.terminal_value.frame][self.terminal_value.key]
        elif self.type == 'self_evaluated':
            calculated_value = root_statistics[self.terminal_value]
        return calculated_value
