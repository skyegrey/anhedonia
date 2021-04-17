from pickle import load
from download_data_from_ec2 import download_data_from_ec2
import shutil
import os
from collections import defaultdict
import matplotlib.pyplot as plt


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
    id_to_asset_on_hand = defaultdict(list)
    id_to_cash_on_hand = defaultdict(list)
    btc_price_over_time = []
    for stat_file in sorted(os.listdir(extraction_directory)):
        stat_file_full_path = f'{extraction_directory}/{stat_file}'

        def get_time_from_stat_file(_stat_file):
            return int(_stat_file.split('_')[1].split('.')[0])

        x_axis.append(get_time_from_stat_file(stat_file))
        with open(stat_file_full_path, 'rb') as pickled_file:
            un_pickled_data = load(pickled_file)
            current_btc_price = un_pickled_data['current_btc_price']
            btc_price_over_time.append(current_btc_price)
            value = un_pickled_data['values']
            asset_on_hand = un_pickled_data['asset_on_hand']
            cash_on_hand = un_pickled_data['cash_on_hand']
            for tree_id, (value_data, asset_data, cash_data) in enumerate(zip(value, asset_on_hand, cash_on_hand)):
                id_to_value_y_axis[tree_id].append(value_data[1])
                id_to_asset_on_hand[tree_id].append(asset_data[1])
                id_to_cash_on_hand[tree_id].append(cash_data[1])

    figure, axis = plt.subplots(2, 2)
    for tree_id in id_to_value_y_axis.keys():
        axis[0, 0].plot(x_axis, id_to_value_y_axis[tree_id])
        axis[0, 0].set_title('Tree Value')
        axis[1, 0].plot(x_axis, id_to_asset_on_hand[tree_id])
        axis[1, 0].set_title('Asset on Hand')
        axis[0, 1].plot(x_axis, btc_price_over_time)
        axis[0, 1].set_title('BTC Price')
        axis[1, 1].plot(x_axis, id_to_cash_on_hand[tree_id])
        axis[1, 1].set_title('Cash on Hand')
    plt.show()


visualize_epoch(run_id='local-viz-compression-4', epoch=3)
