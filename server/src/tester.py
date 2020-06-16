import math

import output_manager
import utils
import visualizer
import data_analyser
import data_extractor
from sklearn.metrics import mean_squared_error
import pandas as pd
import math
import os
import facade


def generate_interpolated_csv_for_test(test_csv_path):
    interpolated_test_csv_path = data_extractor.generate_interpolated_csv(test_csv_path,
                                                                          output_path='../expected_output')
    return interpolated_test_csv_path


# def compare_keypoints(output_dirs_for_test, output_dirs_for_tested_video):
#     interpolated_test_csv_path = generate_interpolated_csv_for_test(output_dirs_for_test)
#     visualizer.show_body_parts_interpolated_location_diff_by_time(output_dirs_for_test, output_dirs_for_tested_video)
#     return interpolated_test_csv_path


def compare_col_from_csv(actual_csv_path, expected_csv_path, col_to_comp, comp_metric=mean_squared_error):
    actual_df = pd.read_csv(actual_csv_path)
    expected_df = pd.read_csv(expected_csv_path)
    actual_kp = actual_df[col_to_comp]
    expected_kp = expected_df[col_to_comp]
    metric_result = comp_metric(expected_kp, actual_kp)
    return metric_result


def compare_avg_angle_from_csv(actual_csv_path, expected_csv_path, col_names):
    actual_avg_angle_dict = data_analyser.calc_avg_angle(actual_csv_path, col_names)
    expected_avg_angle_dict = data_analyser.calc_avg_angle(expected_csv_path, col_names)
    distance_dict = {}
    for key in expected_avg_angle_dict.keys():
        distance_dict[key] = math.fabs(actual_avg_angle_dict[key] - expected_avg_angle_dict[key])
    visualizer.plot_histogram_from_dict({'actual': actual_avg_angle_dict, 'expected': expected_avg_angle_dict},
                                        'Keypoints', 'Average Angle')
    return actual_avg_angle_dict


def start_test(actual_csvs_dir, expected_csvs_dir, output_path,movie_name):
    """ Compare between each pair of csv files from  expected and actual directories.

    :param actual_csvs_dir: Path to actual results directory.
    :param expected_csvs_dir: Path to expected results directory.
    :param output_path: Path to store generated files in.
    :param filename: Movie name for getting expected csv.
    """
    for root, dirs_list, files_list in os.walk(actual_csvs_dir):
        for file_name in files_list:
            filename_without_extension = str(file_name).split('.')[0]
            if os.path.splitext(file_name)[-1] == '.csv':
                expected_match_file = check_for_match_file_in_expected(filename_without_extension,expected_csvs_dir)
                if not expected_match_file is None:
                    actual_csv_path = actual_csvs_dir + '/' + file_name
                    expected_csv_path = expected_csvs_dir + '/' + expected_match_file
                    compare_csvs(actual_csv_path, expected_csv_path, output_path, filename=filename_without_extension)
                    visualizer.plot_multi_graphs_from_other_csvs([expected_csv_path, actual_csv_path],
                                                                 output_path=output_path)

    interpolated_and_filtered_csv_path = actual_csvs_dir + '/interpolated_and_filtered_all_keypoints.csv'
    ground_truth_all_kp = output_manager.get_expected_csv_path_for_movie(movie_name)
    visualizer.plot_multi_graphs_from_other_csvs([ground_truth_all_kp, interpolated_and_filtered_csv_path],
                                                 output_path=output_path)
    row_data_path = actual_csvs_dir + '/all_keypoints.csv'
    visualizer.plot_multi_graphs_from_other_csvs(
        [ground_truth_all_kp, interpolated_and_filtered_csv_path, row_data_path],
        output_path=output_path, name_prefix='expected_vs_interpolated_vs_raw_data')


def check_for_match_file_in_expected(actual_filename, expected_csvs_dir):
    for root, dirs_list, files_list in os.walk(expected_csvs_dir):
        for file_name in files_list:
            filename_without_extension = str(file_name).split('.')[0]
            if filename_without_extension.startswith(actual_filename + '_') and os.path.splitext(file_name)[-1] == '.csv':
                return file_name
    return None


def compare_csvs(actual_csv_path, expected_csv_path, output_path, filename='comparison.csv', tolerance=1,
                 col_names=None):
    """ Gets 2 csvs paths and compare between them. Results are stored in generated csvs.

    :param actual_csv_path: Path to actual results
    :param expected_csv_path: Path to expected results
    :param output_path: Path to store generated files in.
    :param filename: Output file name.
    :param tolerance: Max space for error between 2 records.
    :param col_names: Column names to be compared.
    """
    actual_df = pd.read_csv(actual_csv_path)
    expected_df = pd.read_csv(expected_csv_path)
    if col_names is None:
        col_names = list(expected_df.columns)
        col_names.remove('Frame Number')
    compared_df = pd.DataFrame(columns=col_names)
    tolerated_count = 0
    for idx, expected_row in expected_df.iterrows():
        if expected_row['Frame Number'] not in actual_df['Frame Number'].values:
            continue
        actual_row = actual_df.loc[actual_df['Frame Number'] == expected_row['Frame Number']].iloc[0, :]
        compared_row = {'Frame Number': expected_row['Frame Number'], 'tolerated': 1}
        for col in col_names:
            if math.isnan(expected_row[col]):
                compared_row[col] = 1
            elif math.isnan(actual_row[col]):
                compared_row[col] = 0
            else:
                col_diff = math.fabs(actual_row[col] - expected_row[col])
                if col_diff < tolerance:
                    compared_row[col] = 1
                else:
                    compared_row[col] = 0
            compared_row['tolerated'] = compared_row['tolerated'] and compared_row[col]
        if compared_row['tolerated'] == 1:
            tolerated_count += 1
        compared_df = compared_df.append(compared_row, ignore_index=True)
    compared_df = compared_df.set_index('Frame Number')
    compared_df.to_csv(output_path + '/' + filename + '_accuracy_check.csv', index=False)
    acc_dic = {'accuracy': round(tolerated_count / len(compared_df), 3)}
    for col in col_names:
        acc_dic[col + '_accuracy'] = round(len(compared_df.loc[compared_df[col] == 1]) / len(compared_df), 3)
    accuracy_statistics_df = pd.DataFrame(data=acc_dic, index=[0])
    accuracy_statistics_df.to_csv(output_path + '/' + filename + '_accuracy_statistics.csv')


if __name__ == '__main__':
    actual_path = '<enter actual path>'
    actual_path = os.getcwd() + '/../output/roeegro/MVI_8180_from_frame_0/2020-06-14/20-24-06/analytical_data'
    expected_path = '<enter expected path>'
    expected_path = os.getcwd() + '/../tests/MVI_8180/ground_truth_data'
    output_path = '<enter output path> '
    cols = ['RShoulderX', 'RShoulderY', 'RElbowX', 'RElbowY', 'RWristX', 'RWristY',
            'LShoulderX', 'LShoulderY', 'LElbowX', 'LElbowY', 'LWristX', 'LWristY']
    output_path = os.getcwd() + '/comparison'
    start_test(actual_path, expected_path, output_path, 'MVI_8180')
