from nodes.root_node import RootNode
from nodes.terminal_node import TerminalNode
from random import randint
from collections import namedtuple


class PopulationManager:

    def __init__(self, population_size):
        self.population_size = population_size
        self.real_time_terminals = self.get_real_time_data()
        self.population = self.generate_initial_population()

    def get_real_time_data(self):
        # Get current time
        # Setup API connection
        import urllib.request
        api_key = '9f0216be33fc340939350523f2e6d36f'
        url = f"https://api.nomics.com/v1/currencies/ticker?key={api_key}&ids=BTC&interval=1d,30d&convert=EUR"
        print(urllib.request.urlopen(url).read())
        # Save real time keys
        # Run for max number of open windows
        pass

    def generate_initial_population(self):
        # Select a function to serve as the root of the node
        # Skip this step for now, all nodes are addition based
        NodeFunction = namedtuple('node_function', 'type, max_arity')
        terminals = ['constant']
        node_function = NodeFunction('addition', 5)

        population = []
        for _ in range(self.population_size):
            number_of_nodes = randint(1, node_function.max_arity)
            nodes = [TerminalNode(randint(0, 10)) for _ in range(number_of_nodes)]
            root = RootNode(nodes)
            population.append(root)
        return population

    def generate_next_generation(self):
        self.population = [RootNode([TerminalNode(5)])]

    def sort_population(self):
        self.population.sort(key=lambda tree: self.score_tree(tree), reverse=True)

    def get_best_candidate(self):
        self.sort_population()
        return self.population[0]

    @staticmethod
    def score_tree(tree):
        # Get the decision proposed by the tree for the next frame
        decision = tree.get_decision()

        # Return 0 if purchase is above balance available for the tree, or below balance available to trade
        if decision > tree.purchasing_power:
            return 0

        # Spoof the trade
        if decision < 0:
            return 0

        # Calculate the gain or loss of the trade in EV
        return decision
