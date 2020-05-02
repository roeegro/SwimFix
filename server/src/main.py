# Edited by Roee Groiser
# It requires OpenCV installed for Python
import sys
import os
from sys import platform
import argparse
import facade
import time
import shutil

# import preprocessor
# setup
try:
    # Import Openpose (Windows/Ubuntu/OSX)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    try:
        # Windows Import
        if platform == "win32":
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append(dir_path + '/../openpose/build/python/openpose/Release')
            os.environ['PATH'] = os.environ[
                                     'PATH'] + ';' + dir_path + '/../openpose/build/x64/Release;' + dir_path + '/../openpose/build/bin;'
            import pyopenpose as op

        else:
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append('../../python')
            # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
            # sys.path.append('/usr/local/python')
            # from openpose import pyopenpose as op
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


def wait_analyze_video():
    while True:
        for filename in os.listdir('../videos')[:1]:
            print(filename)
            video_path = '../videos/' + filename
            print(video_path)
            print("Analysing path...")
            all_keypoints_csv_path = facade.get_keypoints_csv_from_video(video_path, params)
            interpolated_keypoints_path = facade.interpolate_and_plot(all_keypoints_csv_path)
            facade.get_angles_csv_from_keypoints_csv(interpolated_keypoints_path)
            facade.get_detected_keypoints_by_frame(all_keypoints_csv_path)
            facade.get_average_swimming_period_from_csv(interpolated_keypoints_path)
            zip_path = facade.zip_output()
            os.remove(video_path)
            print("Removed video")
            # else:
            #     raise ValueError("%s isn't a file!" % filename)
        print("Waiting...")
        time.sleep(1)


if __name__ == '__main__':
    wait_analyze_video()
