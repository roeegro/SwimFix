import data_analyser
import data_extractor
import output_manager
import utils
import visualizer
import evaluator


def filter_and_interpolate(csv_path, video_full_name, y_cols=None, x_col='Frame Number', mult_figures=True,
                           output_path=None):
    """

    :param csv_path: Path to a csv file with all key points coordinates.
    :param video_full_name: full name of video.
    :param y_cols: columns to interpolate.
    :param x_col: Selected index.
    :param mult_figures: True if user wants to compare between more than 1 csv over different columns.
    :param output_path: output path for the outputs of this function.
    :return: Path to the csv that contains interpolated and filtered key points data.
    """
    filtered_and_interpolated_csv_path = data_extractor.filter_and_interpolate(csv_path, output_path=output_path)
    expected_csv_for_movie_path = output_manager.get_excepted_csv_path_for_movie(video_full_name)
    csvs_paths_to_compare = filtered_and_interpolated_csv_path if expected_csv_for_movie_path is None else [
        expected_csv_for_movie_path, filtered_and_interpolated_csv_path]
    visualizer.plot_multi_graphs_from_other_csvs(csvs_paths_to_compare, y_cols, x_col, mult_figures,
                                                 output_path=output_path)
    return filtered_and_interpolated_csv_path


def interpolate_and_plot(csv_path, y_cols=None, x_col='Frame Number', mult_figures=True, filename=None,
                         output_path=None):
    """ Gets path to csv with all key points data and interpolate all columns with body parts coordinates,
        and generates csv file that contains all body part coordinates after interpolation.

    :param csv_path: Path to csv with all key points data
    :param y_cols: Columns to interpolate.
    :param x_col: Selected index.
    :param mult_figures: True if user wants to compare between more than 1 csv over different columns.
    :param filename: File name of the generated csv file.
    :param output_path: Path name of the generated csv file.
    :return: Path to generated csv file that contains all body part coordinates after interpolation.
    """
    interpolated_csv_path = data_extractor.generate_interpolated_csv(csv_path, y_cols, x_col, filename,
                                                                     output_path=output_path)
    visualizer.create_graph(interpolated_csv_path, y_cols, x_col, mult_figures, output_path=output_path)
    return interpolated_csv_path


def create_graph_from_csv(csv_path, y_cols, x_col='Frame Number', mult_figures=True):
    """ Generate graph from csv

    :param csv_path: path to csv that should derive graphs from.
    :param y_cols: columns to plot dependent by x_col.
    :param x_col: column to be the x axis of the graph.
    :param mult_figures: should plot multiple graph.
    """
    visualizer.create_graph(csv_path, y_cols, x_col, mult_figures)


def create_output_dir_for_movie_of_user(video_path, username="guest"):
    """ Generates output directory for given video and the time the user upload it.

    :param video_path: path to video
    :param username: username of the user who requires it.
    """
    video_name = utils.get_file_name(video_path)
    video_name = utils.path_without_suffix(video_name)
    output_manager.generate_dirs_for_output_of_movie(video_name, username=username)


def interpolate_csv(csv_path, y=None, x='Frame Number', output_path=None):
    """ Generates csv with interpolated data and returns its path. Interpolation is done by information taken from csv_path.

    :param csv_path: Path to csv that contains all information about key points.
    :param y: Columns to interpolate.
    :param x: Index of csv.
    :param output_path: Path to the generated csv.
    :return: Path to generated csv.
    """
    return data_extractor.generate_interpolated_csv(csv_path, y, x, output_path=output_path)


def get_angles_csv_from_keypoints_csv(csv_path, avg_angles=True, output_path=None):
    """ Generates csv with angles and returns its path. Extraction of
        angles is done by vectors csv_path.

    :param csv_path: Path to csv contains vectors.
    :param avg_angles: Should calculate average angles
    :param output_path: Path to the generated csv.
    :return: Path to the generated csv.
    """
    angles_csv_path = data_extractor.generate_angles_csv(
        data_extractor.generate_vectors_csv(csv_path, output_path=output_path),
        output_path=output_path)
    if avg_angles:
        avg_angles_dict = data_analyser.calc_avg_angle(angles_csv_path)
        visualizer.plot_scatter_from_dict(avg_angles_dict, 'Keypoints', 'Angle', 'average_keypoints_angles',
                                          output_path=output_path)
        return angles_csv_path
    return angles_csv_path


def get_detected_keypoints_by_frame(csv_path, output_path=None):
    """ Generates csv with indication for detection foreach frame and returns its path.

    :param csv_path: Path to all key points csv.
    :param output_path: Path to generate new csv to.
    :return: Path to generated csv.
    """
    detected_frames_csv_path = data_extractor.generate_detected_keypoints_csv(csv_path, output_path=output_path)
    visualizer.plot_frame_detection(detected_frames_csv_path, output_path=output_path)
    detected_keypoints_dict = data_analyser.calc_detected_frames_count_from_csv(detected_frames_csv_path)
    visualizer.plot_histogram_from_dict(detected_keypoints_dict, 'Keypoints', 'No. of detected frames',
                                        'detected_frames_by_keypoints_histogram', output_path=output_path)
    return detected_keypoints_dict


def get_average_swimming_period_from_csv(csv_path):
    """ Generate csv with average swimming period time and returns its path.

    :param csv_path: Path to all key points csv.
    :return: Path of generated csv.
    """
    return data_analyser.calc_avg_period(csv_path)


def get_keypoints_csv_from_video(video_path, params):
    """ Extracts key points from video path with OpenPose configurations and
        returns the path to all key points csv

    :param video_path: Path to video to be analyzed.
    :param params: Dictionary with OpenPose configurations
    :return: Path to all key points csv
    """
    return data_extractor.get_keypoints_csv_from_video(video_path, params)


def get_output_dir_path(key=None):
    """ Get a path to one of the subdirectories by key."""
    return output_manager.get_output_dir_path(key)


def zip_output():
    """ Creates archeive of the output directory and returns the path to the zip file."""
    zip_path = output_manager.zip_output()
    print('finish to send zip')
    return zip_path


def evaluate_errors(all_kp_path, angles_path, output_name=None):
    evaluator.perfomance_evaluator(all_kp_path, angles_path, output_name)
