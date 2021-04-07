from functools import reduce

from population_manager import PopulationManager
from time import sleep
from logger import logger
from collections import namedtuple, defaultdict
import matplotlib.pyplot as plt
from datetime import datetime
import pickle
import os


log = logger.get_logger(__name__)
config = {
    'run_id': 1,
    'seconds_before_evaluation': 3600,
    'epochs': 100
}

NodeFunction = namedtuple('node_function', 'type function min_arity, max_arity')
TerminalTemplate = namedtuple('TerminalTemplate', 'type value')
population_config = {
    # Logging
    'log_level': 'DEBUG',

    # Hyper parameters
    'population_size': 500,
    'frames': 3600,

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


def graph_over_time(title, trade, epoch_data):
    plt.ion()
    plt.show()
    plt.title(title)
    for tree_label_pair in epoch_data:
        title_to_trade[title][tree_label_pair[0]].append(tree_label_pair[1])

    x_axis = [_ for _ in range(trade + 1)]

    for tree_label_pair in epoch_data:
        y_axis = title_to_trade[title][tree_label_pair[0]]
        plt.plot(x_axis, y_axis)
    
    plt.savefig(f'graphs/latest/Epoch-{epoch}.png')


log.info('Generating initial population')
os.mkdir(f'run_stats/run_{config["run_id"]}')
population_manager = PopulationManager(population_config)
for epoch in range(config['epochs']):
    log.debug('Starting Epoch ', epoch)
    os.mkdir(f'run_stats/run_{config["run_id"]}/epoch_{epoch}')
    title_to_trade = defaultdict(lambda: defaultdict(list))
    time_elapsed = 0
    while time_elapsed < config['seconds_before_evaluation']:
        log.info(f'Trade window time remaining {config["seconds_before_evaluation"] - time_elapsed}')
        trade_start_time = datetime.now()
        log.debug(f'Doing trades')
        population_manager.do_trades()
        stats = population_manager.get_population_statistics()
        log.info(f'Saving stats')
        os.mkdir(f'run_stats/run_{config["run_id"]}/epoch_{epoch}/time_elapsed_{time_elapsed}')
        with open(f'run_stats/run_{config["run_id"]}/epoch_{epoch}/time_elapsed_{time_elapsed}/stats.p', 'wb') as fp:
            pickle.dump(stats, fp, protocol=pickle.HIGHEST_PROTOCOL)

        sleep(1)
        time_elapsed += (datetime.now() - trade_start_time).seconds
        log.info(f'Time Elapsed: {time_elapsed}')

    best_candidate = population_manager.get_best_candidate()
    log.debug('Best Candidate Account Value: ', best_candidate.last_ev)
    log.debug('Best Candidate Cash on hand: ', best_candidate.dollar_count)
    log.debug('Best Candidate Asset on hand: ', best_candidate.asset_count)
    log.debug('Best Candidate last decision: ', best_candidate.last_decision)
    log.debug('Best Candidate attempted decision: ', best_candidate.attempted_last_decision)

    log.debug('Generation average EV: ', population_manager.get_population_statistics()['average_value'])
    log.info('Generating next generation of trees')
    population_manager.generate_next_generation()

# plt.show()
