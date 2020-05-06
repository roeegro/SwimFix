from flask import *
import os
import preprocessor
from shutil import copyfile
import shutil
import time
from datetime import date


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


def upload_file(upload_folder, file):
    create_dir_if_not_exists('partial_movies')
    filename = file.filename
    video_path = os.path.join(upload_folder, filename)
    file.save(video_path)
    new_video_paths = preprocessor.video_cutter(video_path)
    send_file_to_server(new_video_paths)


def get_previous_feedbacks():
    previous_feedbacks = []
    path_to_outputs = './static/output1'
    for filename in os.listdir(path_to_outputs):
        path = path_to_outputs + '/' + str(filename)
        print(path)
        record_dict = dict()
        record_dict['date'] = time.ctime(os.path.getctime(path))
        record_dict['zip'] = path
        record_dict['zip_name'] = filename
        previous_feedbacks.append(record_dict)
    return previous_feedbacks


if __name__ == "__main__":
    app.run(debug=True)
    # serve(app)
