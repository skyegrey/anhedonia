from nodes.root_node import RootNode
from nodes.terminal_node import TerminalNode


class PopulationManager:

    def __init__(self):
        self.population = []

    def generate_next_generation(self):
        self.population = RootNode(TerminalNode(5))

    @staticmethod
    def score_tree(tree):
        # Get the decision proposed by the tree for the next frame
        decision = tree.get_decision()

        # Return 0 if purchase is above balance available for the tree, or below tradeable balance
        if decision > tree.purchasing_power:
            return 0

        # Spoof the trade
        if decision < 0:
            return 0

        # Calculate the gain or loss of the trade in EV
        return 10