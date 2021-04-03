from nodes.root_node import RootNode
from nodes.terminal_node import TerminalNode
from random import choice, uniform, randint
from collections import namedtuple
from logging_decorators import logged_initializer, logged_class_function, logged_class
from collections import defaultdict
from time import sleep


def score_tree(tree, frame_data):
    asset_to_dollar_ratio = 1 / frame_data[0]['dollar_to_asset_ratio']
    tree_value = tree.dollar_count + tree.asset_count * asset_to_dollar_ratio
    tree.last_ev = tree_value

    return tree_value


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
                current_frame_data[key] = float(value)
                current_frame_data['dollar_to_asset_ratio'] = 1 / float(value)
            sleep(config['frame-time'])

        self.logger.debug(f'Frame Data: ', frame_data)
        return frame_data

    @logged_class_function
    def generate_initial_population(self):
        config = {
            'constants_range': (-10, 10),
            'addition_max_arity': 5,
            'subtraction_max_arity': 5
        }
        # Select a function to serve as the root of the node
        # Skip this step for now, all nodes are addition based
        NodeFunction = namedtuple('node_function', 'type function min_arity, max_arity')
        node_functions = [NodeFunction('addition', lambda nodes: sum(nodes), 2, 5),
                          NodeFunction('subtraction', lambda nodes: nodes[0] - sum(nodes[1:]), 2, 5)]

        FrameKeyPair = namedtuple('FrameKeyPair', 'frame key')

        TerminalTemplate = namedtuple('TerminalTemplate', 'type frame_key_pair')
        terminals = [TerminalTemplate('constant', None),
                     TerminalTemplate('run_time_evaluated', FrameKeyPair(0, 'price'))]

        population = []
        for _ in range(self.population_size):
            # Start of individual creation
            root_function = choice(node_functions)

            # Branch here

            # Terminal Filling
            terminals_to_create = randint(root_function.min_arity, root_function.max_arity)
            created_terminals = []
            for _ in range(terminals_to_create):
                terminal_to_create = choice(terminals)
                if terminal_to_create.type == 'constant':
                    constant_value = uniform(*config['constants_range'])
                    created_terminals.append(TerminalNode('constant', constant_value))

                elif terminal_to_create.type == 'run_time_evaluated':
                    created_terminals.append(TerminalNode('run_time_evaluated', terminal_to_create.frame_key_pair))

            root = RootNode(root_function, created_terminals)
            population.append(root)
        return population

    @logged_class_function
    def generate_next_generation(self):
        self.population = []

    @logged_class_function
    def sort_population(self):
        sleep(1)
        frame_data = self.get_real_time_data()
        self.population.sort(key=lambda tree: score_tree(tree, frame_data), reverse=True)

    @logged_class_function
    def get_best_candidate(self):
        self.sort_population()
        return self.population[0]

    @logged_class_function
    def do_trades(self):
        sleep(1)
        frame_data = self.get_real_time_data()
        for tree in self.population:
            decision = tree.get_decision(frame_data)
            tree.dollar_count -= decision
            tree.asset_count += decision*frame_data[0]['dollar_to_asset_ratio']
