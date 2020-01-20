import data_analyser
import data_extractor
import utils
import video_proccesor
import visualizer
import pandas as pd


def interpolate_and_plot(csv_path, y_cols, x_col='Frame Number', interp_csv_path='../output', fig_path='../output',
                         mult_figures=True):
    interpolated_csv_path = data_analyser.create_interpolated_csv(csv_path, y_cols, x_col, interp_csv_path)
    visualizer.create_graph(interpolated_csv_path, y_cols, x_col, fig_path, mult_figures)
    return interpolated_csv_path


def graphs_from_video(video_path, params):
    # for output dirs keys - see utils.generate_dirs_for_output_of_movie
    output_dirs = video_proccesor.get_keypoints_csv_from_video(video_path, params)
    data_extractor.make_body_parts_df(pd.read_csv(output_dirs['analytical_data_path'] + '/all_keypoints.csv'),
                                      output_dirs)
    vectors = pd.read_csv(output_dirs['analytical_data_path'] + '/vectors_by_time.csv')
    data_extractor.make_angle_df(vectors, output_dirs)
    data_extractor.make_body_part_detected_by_frame_df(output_dirs)
    visualizer.create_all_figures(output_dirs)
    utils.zip_output(output_dirs)
    utils.delete_generate_dirs(output_dirs)
