import data_analyser
import data_extractor
import utils
import video_proccesor
import visualizer


def interpolate_and_plot(csv_path, y_cols, x_col='Frame Number', interp_csv_path='../output', fig_path='../output',
                         mult_figures=True):
    interpolated_csv_path = data_extractor.generate_interpolated_csv(csv_path, y_cols, x_col, interp_csv_path)
    visualizer.create_graph(interpolated_csv_path, y_cols, x_col, mult_figures)
    return interpolated_csv_path


def analyze_video(video_path, params):
    # for output dirs keys - see utils.generate_dirs_for_output_of_movie
    all_keypoints_csv_path = data_extractor.get_keypoints_csv_from_video(video_path, params)
    all_keypoints_interpolated_csv_path = interpolate_csv(all_keypoints_csv_path)
    vectors_csv_path = data_extractor.generate_vectors_csv(all_keypoints_interpolated_csv_path)
    angles_csv_path = data_extractor.generate_angles_csv(vectors_csv_path)
    data_extractor.generate_detected_keypoints_csv(all_keypoints_csv_path)
    # visualizer.create_all_figures(output_dirs)
    # utils.zip_output(output_dirs)
    # utils.delete_generate_dirs(output_dirs)


def extract_data_from_vid_and_visualize(video_path):
    output_dirs = utils.generate_dirs_for_output_of_movie(video_path)


def extract_data_from_vid(video_path):
    output_dirs = utils.generate_dirs_for_output_of_movie(video_path)
    all_keypoints_df_csv_path = '../../all_keypoints.csv'
    interpolated_keypoints_csv_path = interpolate_csv(all_keypoints_df_csv_path)
    vectors_csv_path = get_vectors_from_keypoints_csv(interpolated_keypoints_csv_path)
    angles_csv_path = get_angles_from_vectors_csv(vectors_csv_path)
    data_extractor.generate_detected_keypoints_csv(all_keypoints_df_csv_path)
    return 0


def visualize_data_from_csv(csv_path, y_cols=None, x_col='Frame Number', mult_figures=True):
    return visualizer.create_graph(csv_path, y_cols, x_col, mult_figures)


def plot_frame_detection_from_csv(csv_path, y_cols=None, mult_figures=True):
    return visualizer.plot_frame_detection(csv_path, y_cols, mult_figures)


def create_graph_from_csv(csv_path, y_cols, x_col='Frame Number', mult_figures=True):
    visualizer.create_graph(csv_path, y_cols, x_col, mult_figures)


def interpolate_csv(csv_path, y=None, x='Frame Number'):
    return data_extractor.generate_interpolated_csv(csv_path, y, x)


def get_vectors_from_keypoints_csv(keypoints_csv_path, filename='vectors.csv'):
    return data_extractor.generate_vectors_csv(keypoints_csv_path, filename)


def get_angles_from_vectors_csv(vectors_csv_path, filename='angles.csv'):
    return data_extractor.generate_angles_csv(vectors_csv_path, filename)


def get_average_swimming_period_from_csv(csv_path):
    return data_analyser.calc_avg_period(csv_path)


def get_average_angles_from_csv(csv_path):
    return data_analyser.calc_avg_angle(csv_path)


def get_detected_frames_histogram_from_dict(data_dict):
    return visualizer.plot_histogram_from_dict(data_dict)


def main():
    all_keypoints_df_csv_path = '../../all_keypoints.csv'
    video_path = 'MVI_8027.MOV'
    output_dirs = utils.generate_dirs_for_output_of_movie(video_path)
    detected_frames_csv_path = data_extractor.generate_detected_keypoints_csv(all_keypoints_df_csv_path)
    detected_keypoints_dict = data_analyser.calc_detected_frames_count_from_csv(detected_frames_csv_path)
    visualizer.plot_histogram_from_dict(detected_keypoints_dict)


def extract_analyze_plot(video_path):
    return


if __name__ == '__main__':
    main()