from functools import reduce
import shutil
from population_manager import PopulationManager
from time import sleep
from logger import logger
from collections import namedtuple, defaultdict
from datetime import datetime
import pickle
import os


log = logger.get_logger(__name__)
config = {
    'run_id': 'normalize-score-2',
    'seconds_before_evaluation': 5,
    'epochs': 5
}

NodeFunction = namedtuple('node_function', 'type function min_arity, max_arity')
TerminalTemplate = namedtuple('TerminalTemplate', 'type value')
population_config = {
    # Logging
    'log_level': 'DEBUG',

    # Hyper parameters
    'population_size': 500,
    'frames': 5,
    'starting_value': 1000,

    # API Call
    'keys_to_save': ['price', 'market_cap'],
    'seconds-per-frame': 1,
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
    'replacement': .7,
    'recombination': .2,
    'mutation': .1
}

# Setup stat saving
os.umask(0)
run_path = f"run_stats/{config['run_id']}"
os.mkdir(run_path)

log.info('Generating initial population')
population_manager = PopulationManager(population_config)
for epoch in range(config['epochs']):
    log.debug('Starting Epoch ', epoch)

    save_directory = f"{run_path}/epoch_{epoch}"
    os.mkdir(save_directory, 0o777)
    title_to_trade = defaultdict(lambda: defaultdict(list))
    time_elapsed = 0
    while time_elapsed < config['seconds_before_evaluation']:
        # log.info(f"Trading, time left: {config['seconds_before_evaluation'] - time_elapsed}")
        trade_start_time = datetime.now()
        population_manager.do_trades()
        stats = population_manager.get_population_statistics()

        # Save stats of the run
        # log.info(f'Saving stats')
        with open(f'{save_directory}/stats_{time_elapsed}.p', 'wb') as fp:
            pickle.dump(stats, fp, protocol=pickle.HIGHEST_PROTOCOL)

        sleep(1)
        time_elapsed += (datetime.now() - trade_start_time).seconds
        log.info(f'Epoch_{epoch}: Time Elapsed: {time_elapsed}')

    # Display best candidates stats
    # best_candidate = population_manager.get_best_candidate()
    # log.debug(f'Best Candidate Account Value: {best_candidate.last_ev}')
    # log.debug(f'Best Candidate Cash on hand: {best_candidate.dollar_count}')
    # log.debug(f'Best Candidate Asset on hand: {best_candidate.asset_count}')
    # log.debug(f'Best Candidate last decision: {best_candidate.last_decision}')
    # log.debug(f'Best Candidate attempted decision: {best_candidate.attempted_last_decision}')

    # Zip the epoch data
    log.info('Zipping stats')
    output_filename = f"{run_path}/epoch_{epoch}_stats"
    shutil.make_archive(output_filename, 'zip', save_directory)
    # Unlink to save space
    shutil.rmtree(save_directory)

    # log.debug('Generation average EV: ', population_manager.get_population_statistics()['average_value'])
    log.info('Generating next generation of trees')

    population_manager.generate_next_generation()
