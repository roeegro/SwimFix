import os
import shutil
from datetime import datetime

import pandas as pd

from utils import path_without_suffix, get_src_path, get_file_name_for_backslash

expected_output_dirs_dict = {}
output_dirs_dict = {}


def generate_dirs_for_output_of_movie(vid_name, generate_expected=False):
    name = path_without_suffix(vid_name)
    if generate_expected:
        output_dir = get_src_path() + "\\..\\expected_output"
    else:
        output_dir = get_src_path() + "\\..\\output"
    dict_to_return = {}
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    os.chdir(output_dir)
    if not os.path.exists(name):
        os.mkdir(name)
    os.chdir(name)
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
    dict_to_return["output_dir"] = output_dir
    dict_to_return["output_movie_dir"] = output_dir + "\\" + name
    dict_to_return["date_path"] = output_dir + "\\" + name + "\\" + curr_date
    dict_to_return["time_path"] = output_dir + "\\" + name + "\\" + curr_date + "\\" + curr_time
    dict_to_return[
        "analytical_data_path"] = output_dir + "\\" + name + "\\" + curr_date + "\\" + curr_time + "\\" + analytical_data_dir_name
    dict_to_return[
        "figures_path"] = output_dir + "\\" + name + "\\" + curr_date + "\\" + curr_time + "\\" + figures_dir_name
    dict_to_return[
        "frames_path"] = output_dir + "\\" + name + "\\" + curr_date + "\\" + curr_time + "\\" + frames_dir_name
    os.chdir(get_src_path())
    output_dict_key = name + '_' + curr_time + '_' + curr_time
    if generate_expected:
        expected_output_dirs_dict[output_dict_key] = dict_to_return
    else:
        output_dirs_dict[output_dict_key] = dict_to_return
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


def send_zip(src_zip, dest_path, delete_output_folder=False):
    shutil.move(src_zip, dest_path)
    if delete_output_folder:
        delete_generate_dirs()


def get_output_dirs_dict():
    return output_dirs_dict


def get_expected_output_dirs_dict():
    return expected_output_dirs_dict


def get_output_dir(key):
    return output_dirs_dict[key]


def get_expected_output_dir(key):
    return expected_output_dirs_dict[key]


def get_output_csv(key, csv_name='all_keypoints.csv'):
    return output_dirs_dict[key]['analytical_data_path'] + '/' + csv_name


def get_output_figure(key, fig_name):
    return output_dirs_dict[key]['figures_path'] + '/' + fig_name


def get_expected_output_csv(key, csv_name='all_keypoints.csv'):
    return expected_output_dirs_dict[key]['analytical_data_path'] + '/' + csv_name


def get_expected_output_figure(key, fig_name):
    return expected_output_dirs_dict[key]['figures_path'] + '/' + fig_name


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
