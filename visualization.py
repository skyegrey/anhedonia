from pickle import load
from download_data_from_ec2 import download_data_from_ec2
import shutil
from collections import defaultdict
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = [16, 9]
import os


def visualize_epochs(run_id, epochs):
    for epoch in epochs:
        visualize_epoch(run_id, epoch)


def visualize_epoch(run_id, epoch):
    # download_data_from_ec2(run_id, epoch)

    # Unpack local
    epoch_results_path = f"run_stats/{run_id}/epoch_{epoch}_stats.zip"

    # Create space to unpack the file
    extraction_directory = f"run_stats/{run_id}/extracted_epochs/epoch_{epoch}"
    if not os.path.isdir(extraction_directory):
        os.makedirs(extraction_directory)
    shutil.unpack_archive(epoch_results_path, extraction_directory)

    # Read from extracted files
    x_axis = []
    id_to_value_y_axis = defaultdict(list)
    id_to_normalized_value = defaultdict(list)
    id_to_asset_on_hand = defaultdict(list)
    id_to_cash_on_hand = defaultdict(list)

    btc_price_over_time = []
    average_tree_value_over_time = []
    normalized_average_tree_value_over_time = []

    for stat_file in sorted(os.listdir(extraction_directory), key=lambda file_path:
                            int(file_path.split('/')[-1].split('_')[-1].replace('.p', ''))):
        stat_file_full_path = f'{extraction_directory}/{stat_file}'

        def get_time_from_stat_file(_stat_file):
            return int(_stat_file.split('_')[1].split('.')[0])

        x_axis.append(get_time_from_stat_file(stat_file))
        with open(stat_file_full_path, 'rb') as pickled_file:
            un_pickled_data = load(pickled_file)

            # Data not tied to a specific tree
            current_btc_price = un_pickled_data['current_btc_price']
            btc_price_over_time.append(current_btc_price)

            current_average_tree_value = un_pickled_data['average_value']
            average_tree_value_over_time.append(current_average_tree_value)

            current_normalized_average_tree_value = un_pickled_data['normalized_average_value']
            normalized_average_tree_value_over_time.append(current_normalized_average_tree_value)

            # Data tied to specific trees
            value = un_pickled_data['values']
            normalized_value = un_pickled_data['normalized_values']
            asset_on_hand = un_pickled_data['asset_on_hand']
            cash_on_hand = un_pickled_data['cash_on_hand']
            for tree_id, (value_data, normalized_value_data, asset_data, cash_data) \
                    in enumerate(zip(value, normalized_value, asset_on_hand, cash_on_hand)):
                id_to_value_y_axis[tree_id].append(value_data[1])
                id_to_normalized_value[tree_id].append(normalized_value_data[1])
                id_to_asset_on_hand[tree_id].append(asset_data[1])
                id_to_cash_on_hand[tree_id].append(cash_data[1])

    figure, axis = plt.subplots(2, 3)

    for tree_id in id_to_value_y_axis.keys():
        axis[1, 0].plot(x_axis, id_to_value_y_axis[tree_id])
        axis[1, 0].set_title('Tree Value')
        axis[1, 1].plot(x_axis, id_to_normalized_value[tree_id])
        axis[1, 1].set_title('Normalized Tree Value')
        axis[1, 2].plot(x_axis, id_to_asset_on_hand[tree_id])
        axis[1, 2].set_title('Asset on Hand')
        axis[0, 0].plot(x_axis, average_tree_value_over_time)
        axis[0, 0].set_title('Average Tree Value')
        axis[0, 1].plot(x_axis, normalized_average_tree_value_over_time)
        axis[0, 1].set_title('Normalized Average Tree Value')
        axis[0, 2].plot(x_axis, btc_price_over_time)
        axis[0, 2].set_title('BTC Price')
        # axis[1, 1].plot(x_axis, id_to_cash_on_hand[tree_id])
        # axis[1, 1].set_title('Cash on Hand')

    graph_save_directory = f"run_graphs/{run_id}"
    if not os.path.isdir(graph_save_directory):
        os.makedirs(graph_save_directory)

    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
    plt.savefig(f"{graph_save_directory}/epoch_{epoch}_graph.png")
    plt.close('all')


visualize_epochs(run_id='boosted-tree-generation-2', epochs=[i for i in range(50, 150)])
