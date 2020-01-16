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


def main():
    video_proccesor.get_keypoints_csv_from_video(args, params)
    keypoint_with_estimated = data_analyser.keypoint_estimation(pd.read_csv('../output/analytical_data/all_keypoints.csv'))
    keypoint_with_estimated.to_csv('../output/analytical_data/all_keypoints.csv')
    data_analyser.make_body_parts_df(pd.read_csv('../output/analytical_data/all_keypoints.csv'))
    vectors = pd.read_csv('../output/analytical_data/vectors_by_time.csv')
    data_analyser.make_angle_df(vectors)
    data_analyser.make_body_part_detected_by_frame_df()
    visualizer.show_all_figures()


if __name__ == '__main__':
    main()
