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


if __name__ == '__main__':
    start_test()
