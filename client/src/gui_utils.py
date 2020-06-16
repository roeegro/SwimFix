from flask import *
import os
import preprocessor
from shutil import copyfile
import shutil
import time
from zipfile import ZipFile
import pandas as pd


def create_dir_if_not_exists(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
        print('Created dir ' + directory)


def upload_video_file(upload_folder, file, should_take_full_video=False):
    """ Take a video file object and cut it to parts that contains only relevant parts to analyze.

    :param upload_folder: Directory path where video parts are saved and prepared for sending to server.
    :param file: Movie file got from browser.
    :param should_take_full_video: Flag for decision if to cut video or not.
    :return: List of paths to partial videos.
    """
    create_dir_if_not_exists('partial_movies')
    create_dir_if_not_exists(upload_folder)
    filename = file.filename
    video_path = os.path.join(upload_folder, filename)
    file.save(video_path)
    new_video_paths = preprocessor.video_cutter(video_path, should_take_full_video)
    return new_video_paths


def get_all_files_paths(zip_name, found_files_dir_name, extensions_of_files_to_find=[], predicate=None):
    """ Get zip name to search in Client/crc/temp/zip name and extract to other directory in temp 'found_files_dir_name'
        files with specific extension and with specific names.

    :param zip_name:
    :param found_files_dir_name:
    :param extensions_of_files_to_find:
    :param predicate: predicate of desired filenames
    :return: List of files paths in the new directory for future use.
    """
    returned_file_paths = list()
    relative_zip_dir = '/static/temp/'
    if not os.path.exists(os.getcwd() + '/static/temp'):
        os.mkdir(os.getcwd() + '/static/temp')
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
                if predicate is None or predicate(name_of_file_without_extension):  # check if we want this csv
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
            returned_file_paths.append(relative_output_dir + found_files_dir_name + '/{}'.format(file))

    return returned_file_paths


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


def match_error_description_to_frames(swimmer_errors_path):
    """Gets path to swimmer errors map, and returns
    list of dictionaries of errors description and relevant frames."""
    list_of_errors_by_frames_detected = list()
    swimmer_errors_df = pd.read_csv(os.getcwd() + swimmer_errors_path)
    for index, row in swimmer_errors_df.iterrows():
        new_record = {'frames': swimmer_errors_df['frames'][index], 'description': swimmer_errors_df['description'][index], 'points_reduced':swimmer_errors_df['points_reduced'][index]}
        list_of_errors_by_frames_detected.append(new_record)
    return list_of_errors_by_frames_detected


def convert_csv_to_list_of_dicts(csv_path):
    list_of_dicts = list()
    df = pd.read_csv(os.getcwd() + '/' + csv_path)
    for index, row in df.iterrows():
        current_dict = dict()
        for col in list(df.columns):
            current_dict[col] = df[col][index]
        list_of_dicts.append(current_dict)
    return list_of_dicts

if __name__ == '__main__':
    print(convert_csv_to_list_of_dicts('loss_values.csv'))