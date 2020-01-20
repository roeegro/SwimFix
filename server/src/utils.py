import os
from datetime import datetime
import shutil

def filename_without_prefix(filename):
    path_as_array = filename.split('/')
    path_as_array[-1] = path_as_array[-1].split('.')[0]
    output = '/'.join(path_as_array)
    return output


def get_files_in_dir(path):
    directory = os.fsencode(path)
    files = list()
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        files.append(path + "/" + filename)
    return files


def get_id_of_file(path):
    filename = filename_without_prefix(path.split('/')[-1])
    id = filename.split('_')[-1]
    return id


def get_file_name(path):
    return path.split('/')[-1]


def get_file_name_for_backslash(path):
    return path.split('\\')[-1]


def get_number_of_start_frame(movie_name):
    name_parts = movie_name.split('_')
    return int(name_parts[-1])


def get_src_path():
    return os.path.dirname(os.path.realpath(__file__))


def get_body_parts():
    return ['NeckX', 'NeckY', 'NeckScore', 'ChestX', 'ChestY', 'ChestScore', 'RShoulderX', 'RShoulderY',
            'RShoulderScore', 'RElbowX', 'RElbowY', 'RElbowScore', 'RWristX', 'RWristY', 'RWristScore', 'LShoulderX',
            'LShoulderY', 'LShoulderScore',
            'LElbowX', 'LElbowY', 'LElbowScore', 'LWristX', 'LWristY', 'LWristScore']


def generate_dirs_for_output_of_movie(movName):
    outputs_dir = get_src_path() + "\\..\\output"
    os.chdir(outputs_dir)
    time_created = datetime.utcnow().strftime('%d-%m-%Y__%H_%M_%S_%f')[:-3]
    print(time_created)
    movie_output_dir = "{}_{}_output".format(movName, time_created)
    os.mkdir(movie_output_dir)
    os.chdir(".\\" + movie_output_dir)
    analytical_data_path = "analytical_data"
    figures_path = "figures"
    frames = "frames"
    os.mkdir(analytical_data_path)
    os.mkdir(figures_path)
    os.mkdir(frames)
    dict_to_return = dict()
    dict_to_return["output_dir"] = outputs_dir
    dict_to_return["output_movie_dir"] = outputs_dir + "\\" + movie_output_dir
    dict_to_return["analytical_data_path"] = outputs_dir + "\\" + movie_output_dir + "\\" + analytical_data_path
    dict_to_return["figures_path"] = outputs_dir + "\\" + movie_output_dir + "\\" + figures_path
    dict_to_return["frames"] = outputs_dir + "\\" + movie_output_dir + "\\" + frames
    os.chdir(get_src_path())

    return dict_to_return


def zip_output(output_dirs):
    filename = get_file_name_for_backslash(output_dirs['output_movie_dir'])
    shutil.make_archive('{}.zip'.format(filename), 'zip', output_dirs['output_movie_dir'])
    return '{}.zip'.format(filename)


if __name__ == "__main__":
    print(get_src_path())
