from population_manager import PopulationManager

population_manager = PopulationManager()

population_manager.generate_next_generation()
best_candidate = population_manager.get_best_candidate()
