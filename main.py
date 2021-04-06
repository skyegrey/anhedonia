from functools import reduce

from population_manager import PopulationManager
from time import sleep
from logger import logger
from collections import namedtuple

log = logger.get_logger(__name__)
config = {
    'trades_before_evaluation': 60,
    'epochs': 100
}

NodeFunction = namedtuple('node_function', 'type function min_arity, max_arity')
TerminalTemplate = namedtuple('TerminalTemplate', 'type value')
population_config = {
    # Logging
    'log_level': 'ERROR',

    # Hyper parameters
    'population_size': 500,
    'frames': config['trades_before_evaluation'],

    # API Call
    'keys_to_save': ['price'],
    'seconds-per-frame': 1,
    'api_key': '9f0216be33fc340939350523f2e6d36f',


    # Initial Population Generation
    'function_selection_chance': .5,

    # Function Set
    'node_functions': [NodeFunction('addition', lambda nodes: sum(nodes), 2, 5),
                       NodeFunction('subtraction', lambda nodes: nodes[0] - sum(nodes[1:]), 2, 5),
                       NodeFunction('multiplication', lambda nodes: reduce(lambda x, y: x * y, nodes), 2, 5),
                       NodeFunction('protected_division',
                                    lambda nodes: reduce(lambda x, y: x / y if y != 0 else 1, nodes), 2, 5)],

    # Terminal Set
    'constants_range': (-1000, 1000),
    'terminals': [TerminalTemplate('constant', None),
                  TerminalTemplate('run_time_evaluated', 'price'),
                  TerminalTemplate('self_evaluated', 'dollar_count')
                  ],

    # Next generation operation odds
    'replacement': .7,
    'recombination': .2,
    'mutation': .1
}

log.info('Generating initial population')
population_manager = PopulationManager(population_config)
for epoch in range(config['epochs']):
    log.debug('Starting Epoch ', epoch)
    for _ in range(config['trades_before_evaluation']):
        log.info(f'Running Trade {_ + 1} of {config["trades_before_evaluation"]} on trees')
        population_manager.do_trades()

    best_candidate = population_manager.get_best_candidate()
    log.debug('Best Candidate Account Value: ', best_candidate.last_ev)
    log.debug('Best Candidate Cash on hand: ', best_candidate.dollar_count)
    log.debug('Best Candidate Asset on hand: ', best_candidate.asset_count)
    log.debug('Best Candidate last decision: ', best_candidate.last_decision)
    log.debug('Best Candidate attempted decision: ', best_candidate.attempted_last_decision)

    log.debug('Generation average EV: ', population_manager.get_population_statistics()['average_value'])
    log.info('Generating next generation of trees')
    population_manager.generate_next_generation()
