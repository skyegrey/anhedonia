import math
import os
import pickle
import shutil

from nodes.root_node import RootNode
from nodes.terminal_node import TerminalNode
from nodes.function_node import FunctionNode
from random import choice, uniform, randint, random
from collections import namedtuple, defaultdict
from logging_decorators import logged_initializer, logged_class_function, logged_class
from time import sleep
from copy import deepcopy
from datetime import datetime
import urllib.request

from api_manager import ApiManager


def score_tree(tree, frame_data):
    asset_to_dollar_ratio = 1 / frame_data[0]['dollar_to_asset_ratio']
    tree_value = tree.dollar_count + tree.asset_count * asset_to_dollar_ratio
    tree.last_ev = tree_value
    return tree_value


def get_tree_fitness(tree, window, initial_bought_value_asset):
    asset_to_dollar_ratio = 1 / window[0]['dollar_to_asset_ratio']
    tree_value = tree.dollar_count + tree.asset_count * asset_to_dollar_ratio
    normalized_tree_value = tree_value / initial_bought_value_asset

    fitness = normalized_tree_value
    if not tree.traded_cash:
        fitness /= 2
    if not tree.traded_btc:
        fitness /= 2

    return fitness


@logged_class
class PopulationManager:

    @logged_initializer
    def __init__(self, config):
        self.config = config
        self.logger.set_level(self.config['log_level'])
        self.population_size = self.config['population_size']
        self.population = self.generate_initial_population()

        # Initialize api manager -- maybe by reference in the future O:
        self.api_manager = ApiManager(config)

        # Warmup API Manager
        while not self.api_manager.is_warm:
            sleep(1)
        else:
            self.logger.progress('API Manager is warm')

        # Housekeeping for later
        self.population_first_frame_price = None

        # self.catchup_population()

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
    def generate_next_generation(self, window):

        def get_weighted_random_index():
            random_int_range = (self.population_size / 2) * (self.population_size + 1)
            random_choice = randint(0, random_int_range)
            b = 2 * self.population_size + 1
            random_index = math.floor((-b + math.sqrt(b ** 2 - 8 * random_choice)) / (-2))
            return random_index

        # In this step, get fitness alongside the sort
        # sorted_fitness_index_pairs = self.sort_population_with_fitness(window)
        self.sort_population(window)

        # Okay here we go
        next_population = []

        # Take an amount of elites
        elites = 10
        elites_from_last_generation = self.population[:elites]
        next_population.extend(elites_from_last_generation)

        trees_from_last_generation_count = round(self.config['replacement'] * self.population_size) - elites

        # Positionally weighted reselection
        for _ in range(trees_from_last_generation_count):
            next_population.append(self.population[get_weighted_random_index()])

        # Recombination
        trees_to_recombine = round(self.config['recombination'] * self.population_size)

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
        self.population_first_frame_price = None

        self.population = next_population

    @logged_class_function
    def sort_population(self, window):
        initial_buyable_asset = self.config['starting_value'] / self.population_first_frame_price
        initial_bought_value_asset = initial_buyable_asset * window[0]['price']
        self.population.sort(key=lambda tree: get_tree_fitness(tree, window, initial_bought_value_asset), reverse=True)

    # def sort_population_with_fitness(self, window):
    #     fitnesses_with_index = [(get_tree_fitness(tree, window, initial_bought_value_asset), index) for index, tree in enumerate(self.population)]
    #     fitnesses_with_index.sort(key=lambda fitness_index: fitness_index[0], reverse=True)
    #     return fitnesses_with_index

    @logged_class_function
    def get_best_candidate(self, window):
        self.sort_population(window)
        return self.population[0]

    @logged_class_function
    def do_trades(self, window):
        if self.population_first_frame_price is None:
            self.population_first_frame_price = window[0]['price']
        for tree in self.population:
            decision = tree.get_decision(window)
            tree.dollar_count -= decision
            tree.asset_count += decision * window[0]['dollar_to_asset_ratio']

    @logged_class_function
    def get_population_statistics(self, window):
        statistics = {
            'average_value': sum([score_tree(tree, window)
                                  for tree in self.population]) / len(self.population),
            'values': [(index, tree.last_ev) for index, tree in enumerate(self.population)],
            'cash_on_hand': [(index, tree.dollar_count) for index, tree in enumerate(self.population)],
            'asset_on_hand': [(index, tree.asset_count) for index, tree in enumerate(self.population)],
            'current_btc_price': window[0]['price']
        }

        initial_buyable_asset = self.config['starting_value'] / self.population_first_frame_price
        initial_bought_value_asset = initial_buyable_asset * window[0]['price']
        statistics['normalized_average_value'] = statistics['average_value'] / initial_bought_value_asset
        statistics['normalized_values'] = [(index, value / initial_bought_value_asset)
                                           for index, value in statistics['values']]
        return statistics

    def train(self):
        # Setup stat saving
        os.umask(0)
        run_path = f"run_stats/{self.config['run_id']}"
        if not os.path.isdir(run_path):
            os.mkdir(run_path)

        for epoch in range(self.config['epochs']):
            self.logger.progress(f'Starting Epoch {epoch}')

            save_directory = f"{run_path}/epoch_{epoch}"
            if not os.path.isdir(save_directory):
                os.mkdir(save_directory, 0o777)

            # Do catchup trades
            catchup_trade_start_time = datetime.now()
            catchup_window = self.api_manager.get_catchup_window()
            for frame_index in range(self.config['frames']):
                catchup_frame = catchup_window[self.config['frames'] - frame_index:len(catchup_window) - frame_index]
                self.do_trades(catchup_frame)
                stats = self.get_population_statistics(catchup_frame)
                with open(f'{save_directory}/stats_{frame_index}.p', 'wb') as fp:
                    pickle.dump(stats, fp, protocol=pickle.HIGHEST_PROTOCOL)
            catchup_trade_time_elapsed = (datetime.now() - catchup_trade_start_time).seconds
            self.logger.progress(f"{catchup_trade_time_elapsed} seconds of catchup trades")

            # Add in extra catchup frames from evaluation (recursively)

            # Do live trades
            time_elapsed = 0
            window = None
            while time_elapsed < self.config['seconds_before_evaluation']:
                # log.info(f"Trading, time left: {config['seconds_before_evaluation'] - time_elapsed}")
                trade_start_time = datetime.now()
                window = self.api_manager.get_window()
                self.do_trades(window)
                stats = self.get_population_statistics(window)

                # Save stats of the run
                with open(f'{save_directory}/stats_{time_elapsed + self.config["frames"]}.p', 'wb') as fp:
                    pickle.dump(stats, fp, protocol=pickle.HIGHEST_PROTOCOL)

                # TODO On next frame from API manager
                sleep(1)
                time_elapsed += (datetime.now() - trade_start_time).seconds
                self.logger.info(f'Epoch_{epoch}: Time Elapsed: {time_elapsed}')

            # Zip the epoch data
            self.logger.info('Zipping stats')
            output_filename = f"{run_path}/epoch_{epoch}_stats"
            shutil.make_archive(output_filename, 'zip', save_directory)

            # Unlink to save space
            self.logger.info('Removing old stats')
            shutil.rmtree(save_directory)

            # log.debug('Generation average EV: ', population_manager.get_population_statistics()['average_value'])
            self.logger.info('Generating next generation of trees')
            self.generate_next_generation(window)
