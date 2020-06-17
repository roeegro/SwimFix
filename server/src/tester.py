import output_manager
import visualizer
import data_analyser
import data_extractor
import pandas as pd
import math
from sklearn.metrics import mean_squared_error
import os


def generate_interpolated_csv_for_test(test_csv_path):
    interpolated_test_csv_path = data_extractor.generate_interpolated_csv(test_csv_path,
                                                                          output_path='../expected_output')
    return interpolated_test_csv_path


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


def start_test(actual_csvs_dir, expected_csvs_dir, output_path, movie_name):
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
                expected_match_file = check_for_match_file_in_expected(filename_without_extension, expected_csvs_dir)
                if not expected_match_file is None:
                    actual_csv_path = actual_csvs_dir + '/' + file_name
                    expected_csv_path = expected_csvs_dir + '/' + expected_match_file
                    compare_csvs(actual_csv_path, expected_csv_path, output_path, filename=filename_without_extension)
                    visualizer.plot_multi_graphs_from_other_csvs([expected_csv_path, actual_csv_path],
                                                                 output_path=output_path)

    calculate_loss_values(output_path, files_to_search_predicate=lambda
        x: "Ang" in x)  # calculate loss function for angles files only
    interpolated_and_filtered_csv_path = actual_csvs_dir + '/interpolated_and_filtered_all_keypoints.csv'
    ground_truth_all_kp = output_manager.get_expected_csv_path_for_movie(movie_name)
    visualizer.plot_multi_graphs_from_other_csvs([ground_truth_all_kp, interpolated_and_filtered_csv_path],
                                                 output_path=output_path)
    row_data_path = actual_csvs_dir + '/all_keypoints.csv'
    visualizer.plot_multi_graphs_from_other_csvs(
        [ground_truth_all_kp, interpolated_and_filtered_csv_path, row_data_path],
        output_path=output_path, name_prefix='expected_vs_interpolated_vs_raw_data')


def check_for_match_file_in_expected(actual_filename, expected_csvs_dir):
    """ Checks if there is file with matching name x_expected in expected_csvs_dir for acutal file named x.
    :param actual_filename: File name to search match file for.
    :param expected_csvs_dir: Expected files directory to search in
    :return: File name of match file if exists, otherwise None.
    """
    print(os.walk(expected_csvs_dir))
    for root, dirs_list, files_list in os.walk(expected_csvs_dir):
        for file_name in files_list:
            filename_without_extension = str(file_name).split('.')[0]
            if filename_without_extension.startswith(actual_filename + '_') and os.path.splitext(file_name)[
                -1] == '.csv':
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


def calculate_loss_values(output_path, x_col='Frame Number', filename='loss_values.csv',
                          loss_function=lambda expected, acutal: math.sqrt(mean_squared_error(expected, acutal)),
                          files_to_search_predicate=None):
    """ Calculates loss function foreach file in set of files. Generate results into output_path with filename.
        Assumption: Assumes that csvs has 2 columns - first for expected results and the second for actual results.
    :param output_path: Output path to store generated csv in.
    :param x_col: index column.
    :param filename: output file name.
    :param loss_function: Loss function for calculation loss. Default: rmse.
    :param files_to_search_predicate: Filter files according to defined predicate (lambda type)
    """
    file_list = []
    for root, dirs_list, files in os.walk(output_path):
        file_list.extend(files)
        break
    file_list = [file for file in file_list if files_to_search_predicate(file) and file.endswith('.csv')]
    loss_df = pd.DataFrame(columns=['filename', 'loss'])
    for file in file_list:
        path = output_path + '/' + file
        df = pd.read_csv(path).set_index(x_col)
        columns = list(df.columns)
        df = df.fillna(0)  # consider in case that there is no indication
        loss = loss_function(df[columns[0]], df[columns[1]])
        loss_df = loss_df.append({'filename': file, 'loss': loss}, ignore_index=True)

    loss_df.to_csv(output_path + '/' + filename, index=False)
