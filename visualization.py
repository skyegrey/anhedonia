from pickle import Unpickler
import pprint


stat_path = 'run_stats/run_debug_1/epoch_0/time_elapsed_0/stats.p'
with open(stat_path, 'rb') as pickle_file:
    unpickler = Unpickler(pickle_file)
    un_pickled_stats = unpickler.load()

pprint.pprint(un_pickled_stats)
