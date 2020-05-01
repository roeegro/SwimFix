from flask import *
import os
import preprocessor
from shutil import copyfile
import shutil
import time


def create_dir_if_not_exists(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
        print('Created dir' + directory)


def send_file_to_server(video_paths):
    for video_path in video_paths:
        video_name = video_path.split('/')[-1]
        # to create the output dir from the server
        create_dir_if_not_exists('output')
        create_dir_if_not_exists('../../server/videos/')
        copyfile(video_path, "../../server/videos/" + video_name)
        # os.remove(video_path)
        print("Sent file!")
    shutil.rmtree('partial_movies')


def upload_file(upload_folder, file, trimmer=True):
    create_dir_if_not_exists('partial_movies')
    filename = file.filename
    video_path = os.path.join(upload_folder, filename)
    file.save(video_path)
    if trimmer:
        new_video_paths = preprocessor.video_cutter(video_path)
        send_file_to_server(new_video_paths)
    else:
        time.sleep(3)


if __name__ == "__main__":
    app.run(debug=True)
    # serve(app)
