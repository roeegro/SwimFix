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
from client_requests_parser import main_parser
import output_manager
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
            sys.path.append('../openpose/build/python')
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
params["model_pose"] = "COCO"
# params["number_people_max"] = 1

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

# HOST = '84.228.103.80'  # Standard loopback interface address (localhost)
# HOST = '192.168.43.250'  # Standard loopback interface address (localhost)
# HOST = '10.0.0.10'  # Standard loopback interface address (localhost)
HOST = '192.168.2.57'
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)


def accept_request():
    """" Listens to requests from client side."""
    output_manager.generate_data_folders()
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                print(HOST)
                ip = get('https://api.ipify.org').text
                print(ip)
                s.bind((HOST, PORT))
                print('bind. start listening')
                s.listen()
                conn, addr = s.accept()
                with conn:
                    print('Connected by', addr)
                    # while True:
                    data = conn.recv(1024)
                    answer = main_parser(data, conn, params)
                    print('answer is : {}'.format(answer))
                    if not answer:
                        answer = "Done".encode("utf-8")
                    try:
                        conn.sendall(answer)
                    except Exception as e:
                        print(e)
                        continue
        except Exception as e:
            print("An error occurred while trying to process the user's request: ", e)
            continue


if __name__ == '__main__':
    accept_request()
