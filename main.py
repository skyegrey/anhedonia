from population_manager import PopulationManager
from logger import logger

log = logger.get_logger(__name__)
config = {
    'population_size': 100
}

population_manager = PopulationManager(config['population_size'])

best_candidate = population_manager.get_best_candidate()
print(population_manager.score_tree(best_candidate))
