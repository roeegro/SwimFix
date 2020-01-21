import data_analyser
import data_extractor
import utils
import visualizer


def interpolate_and_plot(csv_path, y_cols=None, x_col='Frame Number', mult_figures=True):
    interpolated_csv_path = data_extractor.generate_interpolated_csv(csv_path, y_cols, x_col)
    visualizer.create_graph(interpolated_csv_path, y_cols, x_col, mult_figures)
    return interpolated_csv_path


def create_graph_from_csv(csv_path, y_cols, x_col='Frame Number', mult_figures=True):
    visualizer.create_graph(csv_path, y_cols, x_col, mult_figures)


def interpolate_csv(csv_path, y=None, x='Frame Number'):
    return data_extractor.generate_interpolated_csv(csv_path, y, x)


# def get_vectors_from_keypoints_csv(keypoints_csv_path, filename='vectors.csv'):
#     return data_extractor.generate_vectors_csv(keypoints_csv_path, filename)


# def get_angles_from_vectors_csv(vectors_csv_path, filename='angles.csv'):
#     return data_extractor.generate_angles_csv(vectors_csv_path, filename)


# def get_average_angles_from_csv(csv_path):
#     return data_analyser.calc_avg_angle(csv_path)


# def get_detected_frames_histogram_from_dict(data_dict):
#     return visualizer.plot_histogram_from_dict(data_dict)


def get_angles_csv_from_keypoints_csv(csv_path, interpolate=True, avg_angles=True):
    angles_csv_path = data_extractor.generate_angles_csv(data_extractor.generate_vectors_csv(csv_path))
    if avg_angles:
        avg_angles_dict = data_analyser.calc_avg_angle(angles_csv_path)
        visualizer.plot_histogram_from_dict(avg_angles_dict)
        return avg_angles_dict
    return angles_csv_path


def get_detected_keypoints_by_frame(csv_path, interpolate=False):
    detected_frames_csv_path = data_extractor.generate_detected_keypoints_csv(csv_path)
    visualizer.plot_frame_detection(detected_frames_csv_path)
    detected_keypoints_dict = data_analyser.calc_detected_frames_count_from_csv(detected_frames_csv_path)
    visualizer.plot_histogram_from_dict(detected_keypoints_dict)
    return detected_keypoints_dict


def get_average_swimming_period_from_csv(csv_path, interpolate=True):
    return data_analyser.calc_avg_period(csv_path)


def main():
    all_keypoints_df_csv_path = '../../all_keypoints.csv'
    video_path = 'MVI_8027.MOV'
    output_dirs = utils.generate_dirs_for_output_of_movie(video_path)
    interpolated_keypoints_path = interpolate_and_plot(all_keypoints_df_csv_path)
    get_angles_csv_from_keypoints_csv(interpolated_keypoints_path)
    get_detected_keypoints_by_frame(all_keypoints_df_csv_path)
    get_average_swimming_period_from_csv(interpolated_keypoints_path)


if __name__ == '__main__':
    main()
