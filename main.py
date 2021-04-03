from population_manager import PopulationManager
from time import sleep
from logger import logger

log = logger.get_logger(__name__)
config = {
    'population_size': 100,
    'trades_before_evaluation': 1
}

population_manager = PopulationManager(config['population_size'])

for _ in range(config['trades_before_evaluation']):
    population_manager.do_trades()

best_candidate = population_manager.get_best_candidate()
log.debug('Best Candidate Account Value: ', best_candidate.last_ev)
log.debug('Best Candidate Cash on hand: ', best_candidate.dollar_count)
log.debug('Best Candidate last decision: ', best_candidate.last_decision)
log.debug('Best Candidate attempted decision: ', best_candidate.attempted_last_decision)

