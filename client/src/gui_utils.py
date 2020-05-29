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
        print('Created dir ' + directory)


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


def upload_video_file(upload_folder, file, should_take_full_video=False):
    create_dir_if_not_exists('partial_movies')
    create_dir_if_not_exists(upload_folder)
    filename = file.filename
    video_path = os.path.join(upload_folder, filename)
    file.save(video_path)
    new_video_paths = preprocessor.video_cutter(video_path, should_take_full_video)
    print('new_video_paths : {}'.format(new_video_paths))
    # send_file_to_server(new_video_paths)
    return new_video_paths


def get_all_files_paths(zip_name, found_files_dir_name, extensions_of_files_to_find=[], expected_file_names=None):
    returned_file_paths = list()
    relative_zip_dir = '/static/temp/'
    zip_dir = os.getcwd() + relative_zip_dir
    relative_output_dir = '/static/temp/'
    output_dir = os.getcwd() + relative_output_dir
    if not os.path.exists(output_dir + found_files_dir_name):
        os.makedirs(output_dir + found_files_dir_name)
    else:
        for file in os.listdir(output_dir + found_files_dir_name):
            os.remove(output_dir + found_files_dir_name + '/' + file)
    print('we want to unzip {}.zip'.format(zip_dir + zip_name))
    with ZipFile('{}.zip'.format(zip_dir + zip_name), 'r') as zipObj:
        # Get a list of all archived file names from the zip
        listOfFileNames = zipObj.namelist()
        # Iterate over the file names
        for fileName in listOfFileNames:
            # Check extension
            file_extension = fileName.split('.')[-1]
            if file_extension in extensions_of_files_to_find:
                # Extract a single file from zip
                name_of_file_with_extension = fileName.split('/')[-1]
                name_of_file_without_extension = name_of_file_with_extension.split('.')[0]
                if expected_file_names is None or name_of_file_without_extension in expected_file_names:  # check if we want this csv
                    # print('filename {} , extension {} is extracted'.format(fileName, file_extension))
                    zipObj.extract(fileName, output_dir + found_files_dir_name)
                    try:
                        shutil.move(output_dir + found_files_dir_name + '/{}'.format(fileName),
                                    output_dir + found_files_dir_name)
                    except:
                        continue

    for file in os.listdir(output_dir + found_files_dir_name):
        file_extension = file.split('.')[-1]
        if not file_extension in extensions_of_files_to_find:
            shutil.rmtree(output_dir + found_files_dir_name + '/{}'.format(file))
        else:
            # print(relative_output_dir + found_files_dir_name + '/{}'.format(file))
            returned_file_paths.append(relative_output_dir + found_files_dir_name + '/{}'.format(file))

    return returned_file_paths


def get_previous_feedbacks_groiser():
    previous_feedbacks = []
    path_to_outputs = './static/output'
    for filename in os.listdir(path_to_outputs):
        path = path_to_outputs + '/' + str(filename)
        record_dict = dict()
        record_dict['date'] = time.ctime(os.path.getctime(path))
        record_dict['zip'] = path
        record_dict['zip_name'] = filename
        record_dict['zip_name_without_extension'] = filename.split('.')[0]
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
