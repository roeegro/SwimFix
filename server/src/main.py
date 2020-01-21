# Edited by Roee Groiser
# It requires OpenCV installed for Python
import sys
import os
from sys import platform
import argparse
import pandas as pd
import numpy as np
import visualizer
import video_proccesor
import data_analyser
import data_extractor
import utils

# import preprocessor
# setup
try:
    # Import Openpose (Windows/Ubuntu/OSX)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    try:
        # Windows Import
        if platform == "win32":
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append(dir_path + '/../openpose/build/python/openpose/Release');
            os.environ['PATH'] = os.environ[
                                     'PATH'] + ';' + dir_path + '/../openpose/build/x64/Release;' + dir_path + '/../openpose/build/bin;'
            import pyopenpose as op

        else:
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append('../../python');
            # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
            # sys.path.append('/usr/local/python')
            from openpose import pyopenpose as op
    except:
        print(
            'Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
except:
    print('not valid')

# Flags
parser = argparse.ArgumentParser()
parser.add_argument("--image_path",
                    help="Process an image. Read all standard formats (jpg, png, bmp, etc.).")
args = parser.parse_known_args()

# Custom Params (refer to include/openpose/flags.hpp for more parameters)
params = dict()
params["model_folder"] = "../openpose/models/"

# Add others in path?
for i in range(0, len(args[1])):
    curr_item = args[1][i]
    if i != len(args[1]) - 1:
        next_item = args[1][i + 1]
    else:
        next_item = "1"
    if "--" in curr_item and "--" in next_item:
        key = curr_item.replace('-', '')
        if key not in params:  params[key] = "1"
    elif "--" in curr_item and "--" not in next_item:
        key = curr_item.replace('-', '')
        if key not in params: params[key] = next_item


def interpolate_and_plot(csv_path, y_cols, x_col='Frame Number', interp_csv_path='../output', fig_path='../output', mult_figures=True):
    interpolated_csv_path = data_analyser.create_interpolated_csv(csv_path, y_cols, x_col, interp_csv_path)
    visualizer.create_graph(interpolated_csv_path, y_cols, x_col, fig_path, mult_figures)
    return interpolated_csv_path


def main():
    # interpolate_and_plot('../../all_keypoints.csv', ['RWristY', 'LWristY'], mult_figures=False)
    interp_csv_path = data_analyser.create_interpolated_csv('../../all_keypoints.csv')
    vector_csv_path = data_extractor.generate_vectors_csv(interp_csv_path)
    angles_csv_path = data_extractor.generate_angles_csv(vector_csv_path)
    visualizer.create_graph(angles_csv_path)
    data_extractor.make_body_parts_df(interp_csv_path, {})
    data_extractor.make_angle_df('../output/groiser/groiser_vectors.csv', {})
    visualizer.create_graph('../output/groiser/groiser_angles.csv', output_path='../output/groiser')
    # # for output dirs keys - see utils.generate_dirs_for_output_of_movie
    # output_dirs = video_proccesor.get_keypoints_csv_from_video(args, params)
    # data_extractor.make_body_parts_df(pd.read_csv(output_dirs['analytical_data_path'] + '/all_keypoints.csv'),
    #                                  output_dirs)
    # vectors = pd.read_csv(output_dirs['analytical_data_path'] + '/vectors_by_time.csv')
    # data_extractor.make_angle_df(vectors, output_dirs)
    # data_extractor.make_body_part_detected_by_frame_df(output_dirs)
    # visualizer.create_all_figures(output_dirs)
    # utils.zip_output(output_dirs)
    # utils.delete_generate_dirs(output_dirs)


if __name__ == '__main__':
    main()
