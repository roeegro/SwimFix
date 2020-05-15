from flask import *
import os
import preprocessor
from shutil import copyfile
import shutil
import time
from zipfile import ZipFile

from client.src import mysql


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


def get_all_csvs_paths(zip_name, expected_csvs_names=['all_keypoints', 'angles', 'detected_keypoints',
                                                      'interpolated_all_keypoints']):
    csvs_paths = list()
    relative_zip_dir = '/static/output1/'
    zip_dir = os.getcwd() + relative_zip_dir
    # os.chdir(zip_dir)

    if not os.path.exists('csvs'):
        os.makedirs('csvs')
    else:
        for file in os.listdir(zip_dir + 'csvs'):
            os.remove(zip_dir + 'csvs/' + file)

    with ZipFile('{}.zip'.format(zip_dir + zip_name), 'r') as zipObj:
        # Get a list of all archived file names from the zip
        listOfFileNames = zipObj.namelist()
        # Iterate over the file names
        for fileName in listOfFileNames:
            # Check filename endswith csv
            if fileName.endswith('.csv'):
                # Extract a single file from zip
                name_of_file_with_extension = fileName.split('/')[-1]
                name_of_file_without_extension = name_of_file_with_extension.split('.')[0]
                if name_of_file_without_extension in expected_csvs_names:  # check if we want this csv
                    zipObj.extract(fileName, zip_dir + 'csvs')
                    try:
                        shutil.move(zip_dir + 'csvs/{}'.format(fileName), zip_dir + 'csvs')
                    except:
                        continue
    for file in os.listdir(zip_dir + 'csvs'):
        if not file.endswith('.csv'):
            shutil.rmtree(zip_dir + 'csvs/{}'.format(file))
        else:
            csvs_paths.append(relative_zip_dir + 'csvs/{}'.format(file))

    if len(csvs_paths) == 0:
        shutil.rmtree(zip_dir + 'csvs')
    # os.chdir('../..')
    return zip_dir + 'csvs', csvs_paths


def get_previous_feedbacks_groiser():
    previous_feedbacks = []
    path_to_outputs = './static/output1'
    for filename in os.listdir(path_to_outputs):
        path = path_to_outputs + '/' + str(filename)
        record_dict = dict()
        record_dict['date'] = time.ctime(os.path.getctime(path))
        record_dict['zip'] = path
        record_dict['zip_name'] = filename
        record_dict['zip_name_without_extension'] = filename.split('.')[0]
        previous_feedbacks.append(record_dict)
    return previous_feedbacks


def get_previous_feedbacks(user_id):
    previous_feedbacks = []
    path_to_outputs = './static/output1'
    cur = mysql.connection.cursor()
    cur.execute('''
            SELECT FILES.ID, FILES.NAME, FILES.CREATION_DATE, FILES.CREATORID
            FROM FILES
            WHERE FILES.CREATORID = %s
            ORDER BY FILES.CREATION_DATE;
            ''', (user_id,))
    files = cur.fetchall()
    if not files:
        return []
    print(files)
    users_filenames = [row["NAME"] for row in files]
    users_files_creation = [row["CREATION_DATE"] for row in files]
    for filename in os.listdir(path_to_outputs):
        filename_no_extention = filename.split('.')[0]
        if filename_no_extention not in users_filenames: continue
        path = path_to_outputs + '/' + str(filename)
        record_dict = dict()
        # record_dict['date'] = time.ctime(os.path.getctime(path))
        record_dict['date'] = users_files_creation[users_filenames.index(filename_no_extention)]
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
