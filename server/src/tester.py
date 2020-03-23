import output_manager
import utils
import visualizer
import data_analyser
import data_extractor
from sklearn.metrics import mean_squared_error
import pandas as pd
import math
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


# Evaluation Metric is a numeric score for the performance of the swimmer
# def compare_eval_metric_from_csv(actual_csv_path, expected_csv_path, eval_metric_func):


def compare_avg_angle_from_csv(actual_csv_path, expected_csv_path, col_names):
    actual_avg_angle_dict = data_analyser.calc_avg_angle(actual_csv_path, col_names)
    expected_avg_angle_dict = data_analyser.calc_avg_angle(expected_csv_path, col_names)
    distance_dict = {}
    for key in expected_avg_angle_dict.keys():
        distance_dict[key] = math.fabs(actual_avg_angle_dict[key] - expected_avg_angle_dict[key])
    visualizer.plot_histogram_from_dict({'actual': actual_avg_angle_dict, 'expected': expected_avg_angle_dict},
                                        'Keypoints', 'Average Angle')
    return actual_avg_angle_dict


def start_test(out_path):
    output_dir_name = utils.path_without_suffix(out_path)
    output_dir_name = utils.get_file_name(output_dir_name)
    output_dir_name_split = output_dir_name.split('_')
    output_vid_name = output_dir_name_split[0]
    # test_csv_path = '../expected_output' + output_vid_name +'_expected'
    # interpolated_test_csv = generate_interpolated_csv_for_test()

    # output_manager.generate_dirs_for_output_of_movie(output_vid_name, True)
    # output_vid_date = output_dir_name_split[1]
    # output_vid_time = output_dir_name_split[2]
    # data_key = output_vid_name + '/' + output_vid_date + '/' + output_vid_time
    # test_path_dict = output_manager.get_output_dir(data_key)
    # expected_path_dict = output_manager.get_expected_output_dir(data_key)
    pass


def compare_csvs(actual_csv_path, expected_csv_path, out_path, tolerance=1, col_names=None):
    actual_df = pd.read_csv(actual_csv_path)
    expected_df = pd.read_csv(expected_csv_path)
    if col_names is None:
        col_names = list(expected_df.columns)
        col_names.remove('Frame Number')
    compared_df = pd.DataFrame(columns=col_names)
    for idx, expected_row in expected_df.iterrows():
        if expected_row['Frame Number'] not in actual_df['Frame Number'].values:
            continue
        actual_row = actual_df.loc[actual_df['Frame Number'] == expected_row['Frame Number']].iloc[0, :]
        compared_row = {'Frame Number': expected_row['Frame Number']}
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
        compared_df = compared_df.append(compared_row, ignore_index=True)
    compared_df.to_csv(out_path)


if __name__ == '__main__':
    actual_path = '../output/MVI_8027/2020-01-22/00-58-05-647226/analytical_data/interpolated_all_keypoints.csv'
    expected_path = '../output/MVI_8027/MVI_8027_expected.csv'
    output_path = '../output/MVI_8027/MVI_8027_compared.csv'
    compare_csvs(actual_path, expected_path, output_path)
