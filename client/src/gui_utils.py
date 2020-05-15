from flask import *
import os
import preprocessor
from shutil import copyfile
import shutil
import time
from zipfile import ZipFile


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


def upload_video_file(upload_folder, file):
    create_dir_if_not_exists('partial_movies')
    filename = file.filename
    video_path = os.path.join(upload_folder, filename)
    file.save(video_path)
    new_video_paths = preprocessor.video_cutter(video_path)
    send_file_to_server(new_video_paths)


def get_all_csvs_paths(zip_name, expected_csvs_names = ['all_keypoints','angles','detected_keypoints','interpolated_all_keypoints']):
    csvs_paths = list()
    relative_zip_dir = '/static/output1/'
    zip_dir = os.getcwd() + relative_zip_dir
    os.chdir(zip_dir)

    if not os.path.exists('csvs'):
        os.makedirs('csvs')
    else:
        for file in os.listdir(zip_dir + 'csvs'):
            os.remove(zip_dir + 'csvs/' + file)

    with ZipFile('{}.zip'.format(zip_name), 'r') as zipObj:
        # Get a list of all archived file names from the zip
        listOfFileNames = zipObj.namelist()
        # Iterate over the file names
        for fileName in listOfFileNames:
            # Check filename endswith csv
            if fileName.endswith('.csv'):
                # Extract a single file from zip
                name_of_file_with_extension = fileName.split('/')[-1]
                name_of_file_without_extension = name_of_file_with_extension.split('.')[0]
                if name_of_file_without_extension in expected_csvs_names: # check if we want this csv
                    zipObj.extract(fileName, 'csvs')
                    try:
                        shutil.move('csvs/{}'.format(fileName), 'csvs')
                    except:
                        continue
    for file in os.listdir('csvs'):
        if not file.endswith('.csv'):
            shutil.rmtree('csvs/{}'.format(file))
        else:
            csvs_paths.append(relative_zip_dir + 'csvs/{}'.format(file))

    if len(csvs_paths) == 0:
        shutil.rmtree('csvs')
    os.chdir('../..')
    return zip_dir + 'csvs', csvs_paths


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


def upload_python_file(upload_folder, file):
    try:
        filename = file.filename
        extension = filename.split('.')[-1]
        if extension != 'py':
            return False
        path = os.path.join(upload_folder, filename)
        file.save(path)
        shutil.move(path, '../../server/plug_and_play_functions')
        return True
    except:
        return False


if __name__ == "__main__":
    app.run(debug=True)
    # serve(app)
