from population_manager import PopulationManager
from time import sleep
from logger import logger

log = logger.get_logger(__name__)
config = {
    'population_size': 500,
    'trades_before_evaluation': 10,
    'epochs': 100
}

log.info('Generating initial population')
population_manager = PopulationManager(config['population_size'])
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




