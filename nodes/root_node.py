from nodes.function_node import FunctionNode
from datetime import datetime


class RootNode(FunctionNode):
    """Calculates the amount to invest or sell"""

    def __init__(self, function_data, child_nodes):
        super().__init__(function_data, child_nodes)
        # Approximately 20 of each
        self.dollar_count = 1000
        self.asset_count = 0
        self.max_arity = 10
        self.last_decision = 0
        self.attempted_last_decision = 0
        self.starting_ev = 1000
        self.last_ev = 1000
        self.traded_cash = False
        self.traded_btc = False
        self.time_to_decide = 0

    def reset_cash(self):
        self.dollar_count = 1000
        self.asset_count = 0
        self.last_decision = 0
        self.attempted_last_decision = 0
        self.starting_ev = 1000
        self.last_ev = 1000
        self.time_to_decide = 0
        self.traded_cash = False
        self.traded_btc = False
    
    def get_decision(self, frame_data):
        root_statistics = {
            'dollar_count': self.dollar_count,
            'asset_count': self.asset_count,
            'last_ev': self.last_ev
        }

        starting_calculation_time = datetime.now()
        decision = self.calculate(frame_data, root_statistics)
        time_to_decide = (datetime.now() - starting_calculation_time).microseconds
        self.time_to_decide = time_to_decide

        self.attempted_last_decision = decision

        # If the amount to trade is more than the account has, do not trade
        if decision > self.dollar_count:
            decision = 0

        sellable_amount = self.asset_count * frame_data[0]['price']
        if decision < -sellable_amount:
            decision = 0

        # Stops small trades from happening
        decision_threshold = 100
        if abs(decision) < decision_threshold:
            decision = 0

        self.last_decision = decision
        if decision > 0:
            self.traded_cash = True
        elif decision < 0:
            self.traded_btc = True

        return decision
