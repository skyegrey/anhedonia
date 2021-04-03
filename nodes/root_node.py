from nodes.function_node import FunctionNode


class RootNode(FunctionNode):
    """Calculates the amount to invest or sell"""

    def __init__(self, function_data, child_nodes):
        super().__init__(function_data, child_nodes)
        # Approximately 20 of each
        self.dollar_count = 20
        self.asset_count = 0
        self.max_arity = 10
        self.last_decision = 0
        self.attempted_last_decision = 0
        self.starting_ev = 0
        self.last_ev = 0
    
    def get_decision(self, frame_data):
        decision = self.calculate(frame_data)
        self.attempted_last_decision = decision

        # If the amount to trade is more than the account has, do not trade
        if decision > self.dollar_count:
            decision = 0

        sellable_amount = self.asset_count * frame_data[0]['price']
        if decision < -sellable_amount:
            decision = 0

        # Stops small trades from happening
        decision_threshold = 1
        if abs(decision) < decision_threshold:
            decision = 0

        self.last_decision = decision
        return decision
