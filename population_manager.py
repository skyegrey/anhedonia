from nodes.root_node import RootNode
from nodes.terminal_node import TerminalNode
from nodes.function_node import FunctionNode
from random import choice, uniform, randint, random
from collections import namedtuple
from logging_decorators import logged_initializer, logged_class_function, logged_class
from collections import defaultdict
from time import sleep
from functools import reduce


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
            # Todo: Switch to bottom tested window time
            sleep(config['frame-time'])
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

        self.logger.debug(f'Frame Data: ', frame_data)
        return frame_data

    @logged_class_function
    def generate_initial_population(self):
        config = {
            'constants_range': (-10, 10),
            'addition_max_arity': 5,
            'subtraction_max_arity': 5,
            'function_selection_chance': .5
        }

        NodeFunction = namedtuple('node_function', 'type function min_arity, max_arity')
        node_functions = [NodeFunction('addition', lambda nodes: sum(nodes), 2, 5),
                          NodeFunction('subtraction', lambda nodes: nodes[0] - sum(nodes[1:]), 2, 5),
                          NodeFunction('multiplication', lambda nodes: reduce(lambda x, y: x*y, nodes), 2, 5),
                          NodeFunction('protected_division',
                                       lambda nodes: nodes[0] / nodes[1] if nodes[1] != 0 else 1, 2, 2)
                          ]

        FrameKeyPair = namedtuple('FrameKeyPair', 'frame key')
        TerminalTemplate = namedtuple('TerminalTemplate', 'type frame_key_pair')
        terminals = [TerminalTemplate('constant', None),
                     TerminalTemplate('run_time_evaluated', FrameKeyPair(0, 'price'))]

        population = []
        for specimen_count in range(self.population_size):

            def get_terminal():
                terminal_to_create = choice(terminals)

                terminal_type_to_value = {
                    'constant': uniform(*config['constants_range']),
                    'run_time_evaluated': terminal_to_create.frame_key_pair
                }

                terminal_value = terminal_type_to_value[terminal_to_create.type]

                return TerminalNode(terminal_to_create.type, terminal_value)

            def get_function_node(depth, max_depth):
                function_type = choice(node_functions)
                argument_count = randint(function_type.min_arity, function_type.max_arity)

                if depth == max_depth:
                    function_nodes = [get_terminal() for _ in range(argument_count)]

                else:
                    function_nodes = []
                    for _ in range(argument_count):
                        function_selection_roll = random()
                        if function_selection_roll < config['function_selection_chance']:
                            function_nodes.append(get_function_node(depth + 1, max_depth))
                        else:
                            function_nodes.append(get_terminal())

                return FunctionNode(function_type, function_nodes) \
                    if depth != 0 else RootNode(function_type, function_nodes)

            if specimen_count < 50:
                population.append(get_function_node(0, 1))
            elif specimen_count < 75:
                population.append(get_function_node(0, 2))
            elif specimen_count < 90:
                population.append(get_function_node(0, 3))
            else:
                population.append(get_function_node(0, 4))
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
