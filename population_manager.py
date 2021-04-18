import math
from nodes.root_node import RootNode
from nodes.terminal_node import TerminalNode
from nodes.function_node import FunctionNode
from random import choice, uniform, randint, random
from collections import namedtuple
from logging_decorators import logged_initializer, logged_class_function, logged_class
from time import sleep
from copy import deepcopy
from datetime import datetime
import urllib.request
from json import loads


def score_tree(tree, frame_data):
    asset_to_dollar_ratio = 1 / frame_data[0]['dollar_to_asset_ratio']
    tree_value = tree.dollar_count + tree.asset_count * asset_to_dollar_ratio
    tree.last_ev = tree_value

    return tree_value


@logged_class
class PopulationManager:

    @logged_initializer
    def __init__(self, config):
        self.config = config
        self.logger.set_level(self.config['log_level'])
        self.population_size = self.config['population_size']
        self.population = self.generate_initial_population()
        self.last_access_time = None
        self.logger.debug('Start time', self.last_access_time)
        self.data_window = self.get_real_time_data()
        self.first_frame_price = None

    @logged_class_function
    def get_real_time_data(self):
        if self.last_access_time is None:
            frames_to_collect = self.config['frames']
            previous_frames = []

        else:
            frames_to_collect = (datetime.now() - self.last_access_time).seconds
            if frames_to_collect > self.config['frames']:
                frames_to_collect = self.config['frames']
                previous_frames = []
            else:
                previous_frames = self.data_window[frames_to_collect:]

        self.logger.debug(f'Frames to collect {frames_to_collect}')
        # Get current time
        # Setup API connection
        url = f"https://api.nomics.com/v1/currencies/ticker?key={self.config['api_key']}" \
              f"&ids=BTC&interval=1d,30d&convert=EUR"

        collected_frames = []
        for frame in range(frames_to_collect):
            self.logger.debug(f'Collecting data from frame {frame}')
            api_call_start_time = datetime.now()

            max_api_tries = 25
            for _ in range(max_api_tries):
                try:
                    request_return = urllib.request.urlopen(url, timeout=10).read().decode()
                    break
                except:
                    self.logger.error('Failed to get frame data, retrying')
                    sleep(1)
                    continue
            else:
                self.logger.fatal('API Tries maxed out, no response received')
                raise NotImplementedError()

            stripped_request_return = request_return[1:-2]
            request = loads(stripped_request_return)

            frame_data = {}
            for key in self.config['keys_to_save']:
                value = request[key]
                frame_data[key] = float(value)
                frame_data['dollar_to_asset_ratio'] = 1 / float(value)
                collected_frames.append(frame_data)
            microseconds_elapsed = (datetime.now() - api_call_start_time).microseconds
            seconds_to_sleep = self.config['seconds-per-frame'] - microseconds_elapsed / 1000000
            if seconds_to_sleep > 0:
                sleep(seconds_to_sleep)

        collected_frames.extend(previous_frames)
        self.last_access_time = datetime.now()
        return collected_frames

    def get_terminal(self):
        terminal_to_create = choice(self.config['terminals'])

        if terminal_to_create.type == 'constant':
            terminal_value = uniform(*self.config['constants_range'])
        elif terminal_to_create.type == 'run_time_evaluated':
            FrameKeyPair = namedtuple('FrameKeyPair', 'frame key')
            frame = randint(0, self.config['frames'] - 1)
            terminal_value = FrameKeyPair(frame, terminal_to_create.value)
        else:
            terminal_value = terminal_to_create.value

        return TerminalNode(terminal_to_create.type, terminal_value)

    def get_function_node(self, depth, max_depth):
        function_type = choice(self.config['node_functions'])
        argument_count = randint(function_type.min_arity, function_type.max_arity)

        if depth == max_depth:
            function_nodes = [self.get_terminal() for _ in range(argument_count)]

        else:
            function_nodes = []
            for _ in range(argument_count):
                function_selection_roll = random()
                if function_selection_roll < self.config['function_selection_chance']:
                    function_nodes.append(self.get_function_node(depth + 1, max_depth))
                else:
                    function_nodes.append(self.get_terminal())

        return FunctionNode(function_type, function_nodes) \
            if depth != 0 else RootNode(function_type, function_nodes)

    @logged_class_function
    def generate_initial_population(self):
        population = []
        for specimen_count in range(self.population_size):

            if specimen_count < 250:
                population.append(self.get_function_node(0, 1))
            elif specimen_count < 325:
                population.append(self.get_function_node(0, 2))
            elif specimen_count < 387:
                population.append(self.get_function_node(0, 3))
            else:
                population.append(self.get_function_node(0, 4))
        return population

    @logged_class_function
    def generate_next_generation(self):
        self.sort_population()

        # Okay here we go
        next_population = []
        trees_from_last_generation_count = round(self.config['replacement'] * self.population_size)

        # For now, just take elites
        trees_from_last_generation = self.population[:trees_from_last_generation_count]
        next_population.extend(trees_from_last_generation)

        # Recombination
        trees_to_recombine = round(self.config['recombination'] * self.population_size)

        def get_weighted_random_index():
            random_int_range = (self.population_size / 2) * (self.population_size + 1)
            random_choice = randint(0, random_int_range)
            b = 2 * self.population_size + 1
            random_index = math.floor((-b + math.sqrt(b ** 2 - 8 * random_choice)) / (-2))
            return random_index

        def get_all_function_nodes(tree, nodes=None):
            if type(tree) == TerminalNode:
                return
            elif nodes is None:
                nodes = [tree]

            for node in tree.child_nodes:
                if type(node) == FunctionNode:
                    nodes.append(node)
                    get_all_function_nodes(node, nodes)

            return nodes

        def get_all_nodes(tree, nodes=None):
            if nodes is None:
                nodes = [tree]

            for node in tree.child_nodes:
                if type(node) == FunctionNode:
                    nodes.append(node)
                    get_all_nodes(node, nodes)
                elif type(node) == TerminalNode:
                    nodes.append(node)

            return nodes

        for _ in range(trees_to_recombine):
            # Select parents
            parent_1 = deepcopy(self.population[get_weighted_random_index()])
            parent_2 = deepcopy(self.population[get_weighted_random_index()])

            # Get all nodes
            parent_1_function_nodes = get_all_function_nodes(parent_1)
            parent_2_nodes = get_all_nodes(parent_2)

            # Select recombination point from parent 1
            parent_1_recombination_point = choice(parent_1_function_nodes)
            parent_2_recombination_point = choice(parent_2_nodes)

            # Combine trees
            replacement_index = randint(0, len(parent_1_recombination_point.child_nodes) - 1)
            parent_1_recombination_point.child_nodes[replacement_index] = parent_2_recombination_point

            # Add to list of trees
            recombined_tree = parent_1
            next_population.append(recombined_tree)

        trees_to_mutate = round(self.population_size * self.config['mutation'])
        for _ in range(trees_to_mutate):
            tree_to_mutate = deepcopy(self.population[get_weighted_random_index()])
            parent_mutation_node = choice(get_all_function_nodes(tree_to_mutate))
            mutation_index = randint(0, len(parent_mutation_node.child_nodes) - 1)
            new_node = self.get_function_node(3, 4)
            parent_mutation_node.child_nodes[mutation_index] = new_node
            next_population.append(tree_to_mutate)

        leftover_trees = self.population_size - len(next_population)
        # Just take more copies of elites to fill the gap
        next_population.extend(self.population[:leftover_trees])

        # Housekeeping
        [tree.reset_cash() for tree in next_population]
        self.first_frame_price = None

        self.population = next_population

    @logged_class_function
    def sort_population(self):
        frame_data = self.get_real_time_data()
        self.population.sort(key=lambda tree: score_tree(tree, frame_data), reverse=True)

    @logged_class_function
    def get_best_candidate(self):
        self.sort_population()
        return self.population[0]

    @logged_class_function
    def do_trades(self):
        self.data_window = self.get_real_time_data()
        if self.first_frame_price is None:
            self.first_frame_price = self.data_window[0]['price']
        for tree in self.population:
            decision = tree.get_decision(self.data_window)
            tree.dollar_count -= decision
            tree.asset_count += decision * self.data_window[0]['dollar_to_asset_ratio']

    @logged_class_function
    def get_population_statistics(self):
        statistics = {
            'average_value': sum([score_tree(tree, self.data_window)
                                  for tree in self.population]) / len(self.population),
            'values': [(index, tree.last_ev) for index, tree in enumerate(self.population)],
            'cash_on_hand': [(index, tree.dollar_count) for index, tree in enumerate(self.population)],
            'asset_on_hand': [(index, tree.asset_count) for index, tree in enumerate(self.population)],
            'current_btc_price': self.data_window[0]['price']
        }

        initial_buyable_asset = self.config['starting_value'] / self.first_frame_price
        initial_bought_value_asset = initial_buyable_asset * self.data_window[0]['price']
        statistics['normalized_average_value'] = statistics['average_value'] / initial_bought_value_asset
        statistics['normalized_values'] = [(index, value / initial_bought_value_asset)
                                           for index, value in statistics['values']]

        return statistics
