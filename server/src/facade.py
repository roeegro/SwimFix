import data_analyser
import data_extractor
import output_manager
import utils
import visualizer
import os


def interpolate_and_plot(csv_path, y_cols=None, x_col='Frame Number', mult_figures=True, filename=None):
    interpolated_csv_path = data_extractor.generate_interpolated_csv(csv_path, y_cols, x_col, filename)
    visualizer.create_graph(interpolated_csv_path, y_cols, x_col, mult_figures)
    return interpolated_csv_path


def create_graph_from_csv(csv_path, y_cols, x_col='Frame Number', mult_figures=True):
    visualizer.create_graph(csv_path, y_cols, x_col, mult_figures)


def create_output_dir_for_movie_of_user(video_path, username="defaultUser"):
    video_name = utils.get_file_name(video_path)
    video_name = utils.path_without_suffix(video_name)
    output_manager.generate_dirs_for_output_of_movie(video_name, username=username)


def interpolate_csv(csv_path, y=None, x='Frame Number'):
    return data_extractor.generate_interpolated_csv(csv_path, y, x)


def get_angles_csv_from_keypoints_csv(csv_path, avg_angles=True):
    angles_csv_path = data_extractor.generate_angles_csv(data_extractor.generate_vectors_csv(csv_path))
    if avg_angles:
        avg_angles_dict = data_analyser.calc_avg_angle(angles_csv_path)
        visualizer.plot_scatter_from_dict(avg_angles_dict, 'Keypoints', 'Angle', 'average_keypoints_angles')
        return avg_angles_dict
    return angles_csv_path


def get_detected_keypoints_by_frame(csv_path):
    detected_frames_csv_path = data_extractor.generate_detected_keypoints_csv(csv_path)
    visualizer.plot_frame_detection(detected_frames_csv_path)
    detected_keypoints_dict = data_analyser.calc_detected_frames_count_from_csv(detected_frames_csv_path)
    visualizer.plot_histogram_from_dict(detected_keypoints_dict, 'Keypoints', 'No. of detected frames',
                                        'detected_frames_by_keypoints_histogram')
    return detected_keypoints_dict


def get_average_swimming_period_from_csv(csv_path, interpolate=True):
    return data_analyser.calc_avg_period(csv_path)


def get_keypoints_csv_from_video(video_path, params):
    return data_extractor.get_keypoints_csv_from_video(video_path, params)


def get_output_dir_path(key=None):
    return output_manager.get_output_dir_path(key)


def zip_output():
    zip_path = output_manager.zip_output()
    output_manager.send_zip(zip_path, "../../client/src/static/output")
    print('finish to send zip')
    return zip_path


def main():
    all_keypoints_df_csv_path = '../../all_keypoints.csv'
    video_path = 'MVI_8027.MOV'
    # output_dirs = output_manager.generate_dirs_for_output_of_movie(video_path)
    interpolated_keypoints_path = interpolate_and_plot(all_keypoints_df_csv_path)
    get_angles_csv_from_keypoints_csv(interpolated_keypoints_path)
    get_detected_keypoints_by_frame(all_keypoints_df_csv_path)
    get_average_swimming_period_from_csv(interpolated_keypoints_path)


if __name__ == '__main__':
    main()
