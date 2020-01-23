import os
from datetime import datetime
import shutil
import pandas as pd

output_dirs_dict = {}
expected_output_dirs_dict = {}


def filename_without_suffix(path):
    path_as_array = path.split('/')
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
    filename = filename_without_suffix(path.split('/')[-1])
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


def generate_dirs_for_output_of_movie(vid_name, generate_expected=False):
    name = filename_without_suffix(vid_name)
    if generate_expected:
        dict_to_return = expected_output_dirs_dict
    else:
        dict_to_return = output_dirs_dict
    outputs_dir = get_src_path() + "\\..\\output"
    if not os.path.exists(outputs_dir):
        os.mkdir(outputs_dir)
    os.chdir(outputs_dir)
    if not os.path.exists(name):
        os.mkdir(name)
    os.chdir(name)
    # time_created = datetime.utcnow().strftime('%d-%m-%Y__%H_%M_%S_%f')[:-3]
    # time_created = datetime.date().strftime('%d-%m-%Y__%H_%M_%S_%f')[:-3]
    date = datetime.now()
    curr_date = date.strftime('%Y-%m-%d')
    if not os.path.exists(curr_date):
        os.mkdir(curr_date)
    os.chdir(curr_date)
    curr_time = date.strftime('%H-%M-%S-%f')
    if not os.path.exists(curr_time):
        os.mkdir(curr_time)
    os.chdir(curr_time)
    analytical_data_dir_name = "analytical_data"
    figures_dir_name = "figures"
    frames_dir_name = "frames"
    os.mkdir(analytical_data_dir_name)
    os.mkdir(figures_dir_name)
    os.mkdir(frames_dir_name)
    dict_to_return["output_dir"] = outputs_dir
    dict_to_return["output_movie_dir"] = outputs_dir + "\\" + name
    dict_to_return["date_path"] = outputs_dir + "\\" + name + "\\" + curr_date
    dict_to_return["time_path"] = outputs_dir + "\\" + name + "\\" + curr_date + "\\" + curr_time
    dict_to_return[
        "analytical_data_path"] = outputs_dir + "\\" + name + "\\" + curr_date + "\\" + curr_time + "\\" + analytical_data_dir_name
    dict_to_return[
        "figures_path"] = outputs_dir + "\\" + name + "\\" + curr_date + "\\" + curr_time + "\\" + figures_dir_name
    dict_to_return[
        "frames_path"] = outputs_dir + "\\" + name + "\\" + curr_date + "\\" + curr_time + "\\" + frames_dir_name
    os.chdir(get_src_path())
    return dict_to_return


def zip_output():
    filename = get_file_name_for_backslash(output_dirs_dict['output_movie_dir'])
    zip_out_path = output_dirs_dict['time_path']
    os.chdir(zip_out_path)
    time_path = output_dirs_dict['time_path'].split('\\')[-1]
    date_path = output_dirs_dict['date_path'].split('\\')[-1]
    zip_name = '{}_{}_{}'.format(filename, date_path, time_path)
    shutil.make_archive(zip_name, 'zip')
    os.chdir(get_src_path())
    return zip_out_path + '\\{}.zip'.format(zip_name)


def delete_generate_dirs():
    shutil.rmtree(output_dirs_dict['output_movie_dir'])


def keypoint_to_score(col_name):
    if col_name[-1] == 'X' or col_name[-1] == 'Y':
        return col_name[:-1] + 'Score'
    elif 'Score' in col_name:
        return col_name
    return col_name + 'Score'


def get_analytics_dir():
    return output_dirs_dict['analytical_data_path']


def get_figures_dir():
    return output_dirs_dict['figures_path']


def analytical_df_to_csv(df, filename):
    analytical_dir_path = output_dirs_dict['analytical_data_path']
    outp_path = analytical_dir_path + '/' + filename
    pd.DataFrame.to_csv(df, outp_path, index=False)
    return outp_path


def get_frames_dir():
    return output_dirs_dict['frames_path']


def get_output_dirs_dict():
    return output_dirs_dict


def send_zip(src_zip, dest_path, delete_output_folder=False):
    shutil.move(src_zip, dest_path)
    if delete_output_folder:
        delete_generate_dirs()


if __name__ == "__main__":
    print(get_src_path())
