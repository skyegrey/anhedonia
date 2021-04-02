from nodes.root_node import RootNode
from nodes.terminal_node import TerminalNode
from random import randint
from collections import namedtuple
from logging_decorators import logged_initializer, logged_class_function, logged_class
from collections import defaultdict
from time import sleep


@logged_class
class PopulationManager:

    @logged_initializer
    def __init__(self, population_size):
        self.population_size = population_size
        self.real_time_terminals = self.get_real_time_data()
        self.population = self.generate_initial_population()

    @logged_class_function
    def get_real_time_data(self):
        config = {
            'keys_to_save': ['price'],
            'frames': 1,
            'frame-time': 1
        }
        # Get current time
        # Setup API connection
        import urllib.request
        from json import loads
        api_key = '9f0216be33fc340939350523f2e6d36f'
        url = f"https://api.nomics.com/v1/currencies/ticker?key={api_key}&ids=BTC&interval=1d,30d&convert=EUR"

        frame_data = defaultdict(dict)
        for frame in range(config['frames']):
            self.logger.debug(f'Collecting data from frame: ', frame)
            request_return = urllib.request.urlopen(url).read().decode()
            stripped_request_return = request_return[1:-2]
            request = loads(stripped_request_return)
            for key in config['keys_to_save']:
                self.logger.debug(f'Collecting data for key: ', key)
                current_frame_data = frame_data[frame]
                value = request[key]
                self.logger.debug(f'{key} value: ', value)
                current_frame_data[key] = value
            sleep(config['frame-time'])

        self.logger.debug(f'Frame Data: ', frame_data)
        return frame_data

    @logged_class_function
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

    @logged_class_function
    def generate_next_generation(self):
        self.population = [RootNode([TerminalNode(5)])]

    @logged_class_function
    def sort_population(self):
        sleep(1)
        frame_data = self.get_real_time_data()
        dollar_to_asset_ratio = 1 / frame_data[0]['price']
        self.population.sort(key=lambda tree: self.score_tree(tree, dollar_to_asset_ratio), reverse=True)

    @logged_class_function
    def get_best_candidate(self):
        self.sort_population()
        return self.population[0]

    def score_tree(self, tree, dollar_to_asset_ratio):
        tree_value = tree.purchasing_power + tree.asset_count * dollar_to_asset_ratio

        # Calculate the gain or loss of the trade in EV
        return tree_value



