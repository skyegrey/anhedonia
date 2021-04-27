from functools import reduce
from population_manager import PopulationManager
from logger import logger
from collections import namedtuple, defaultdict


log = logger.get_logger(__name__)

NodeFunction = namedtuple('node_function', 'type function min_arity, max_arity')
TerminalTemplate = namedtuple('TerminalTemplate', 'type value')
population_config = {
    'run_id': 'window-catchup-trade-sliding',
    'seconds_before_evaluation': 1,
    'epochs': 5,

    # Logging
    'log_level': 'DEBUG',

    # Hyper parameters
    'population_size': 500,
    'frames': 20,
    'starting_value': 1000,

    # API Call
    'keys_to_save': ['price', 'market_cap'],
    'api_key': '9f0216be33fc340939350523f2e6d36f',

    # Initial Population Generation
    'function_selection_chance': .5,

    # Function Set
    'node_functions': [NodeFunction('addition', lambda nodes: sum(nodes), 2, 2),
                       NodeFunction('subtraction', lambda nodes: nodes[0] - sum(nodes[1:]), 2, 2),
                       NodeFunction('multiplication', lambda nodes: reduce(lambda x, y: x * y, nodes), 2, 2),
                       NodeFunction('protected_division',
                                    lambda nodes: reduce(lambda x, y: x / y if y != 0 else 1, nodes), 2, 2),
                       NodeFunction('max', lambda nodes: max(nodes), 2, 2),
                       NodeFunction('min', lambda nodes: min(nodes), 2, 2)],

    # Terminal Set
    'constants_range': (-1000, 1000),
    'terminals': [TerminalTemplate('constant', None),
                  TerminalTemplate('run_time_evaluated', 'price'),
                  TerminalTemplate('run_time_evaluated', 'market_cap'),
                  TerminalTemplate('self_evaluated', 'dollar_count'),
                  TerminalTemplate('self_evaluated', 'asset_count'),
                  TerminalTemplate('self_evaluated', 'last_ev')
                  ],

    # Next generation operation odds
    'replacement': .9,
    'recombination': .09,
    'mutation': .01
}

log.info('Generating initial population')
population_manager = PopulationManager(population_config)
population_manager.train()
