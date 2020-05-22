# Edited by Roee Groiser
# It requires OpenCV installed for Python
import sys
import os
from sys import platform
import argparse
import facade
import time
import shutil
import socket
import MySQLdb
from requests import get

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

HOST = '10.0.0.12'  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

MYSQL_HOST = '65.19.141.67'
MYSQL_PORT = 3306
MYSQL_USER = 'lironabr'
MYSQL_PASSWORD = 'h3dChhmg'
MYSQL_DB = 'lironabr_swimming_project'
MYSQL_CURSORCLASS = 'DictCursor'
mysql = MySQLdb.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, passwd=MYSQL_PASSWORD, db=MYSQL_DB)


def wait_analyze_video():
    while True:
        for filename in os.listdir('../videos')[:1]:
            video_path = '../videos/' + filename
            try:
                print("Analysing path...")
                facade.create_output_dir_for_movie_of_user(video_path)
                all_keypoints_csv_path = facade.get_keypoints_csv_from_video(video_path, params)
                interpolated_keypoints_path = facade.interpolate_and_plot(all_keypoints_csv_path)
                facade.get_angles_csv_from_keypoints_csv(interpolated_keypoints_path)
                facade.get_detected_keypoints_by_frame(all_keypoints_csv_path)
                facade.get_average_swimming_period_from_csv(interpolated_keypoints_path)
                zip_path = facade.zip_output()
                print('Zipped the output in path: ', zip_path)
                # else:
                #     raise ValueError("%s isn't a file!" % filename)
            except Exception as e:
                print("Server got an error while processing video {} : {}".format(filename, e))
            finally:
                os.remove(video_path)
                print("Removed video")
        print("Waiting...")
        time.sleep(1)


def request_parser(data):
    print(data)
    # print('Users data in db')
    # cur = mysql.cursor()
    # cur.execute("SELECT * FROM USERS")
    # res = cur.fetchall()
    # print(res)


def accept_request():
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(HOST)
            ip = get('https://api.ipify.org').text
            print(ip)
            s.bind((HOST, PORT))
            print('bind. start listening')
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    request_parser(data)
                    if not data:
                        break
                    conn.sendall(data)


if __name__ == '__main__':
    # wait_analyze_video()
    accept_request()
