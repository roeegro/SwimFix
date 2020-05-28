import os
import shutil
from datetime import datetime
import utils
import pandas as pd
from utils import get_src_path, get_file_name_for_backslash

expected_output_dirs_dict = {}
output_dirs_dict = {}


def generate_dirs_for_output_of_movie(movName, username='guest'):
    video_name = utils.path_without_suffix(movName)
    new_output_dirs_dict = dict()
    outputs_dir = get_src_path() + "/../output"
    if not os.path.exists(outputs_dir):
        os.mkdir(outputs_dir)
    os.chdir(outputs_dir)
    if not os.path.exists(username):
        os.mkdir(username)
    os.chdir(username)
    if not os.path.exists(video_name):
        os.mkdir(video_name)
    os.chdir(video_name)
    date = datetime.now()
    curr_date = date.strftime('%Y-%m-%d')

    if not os.path.exists(curr_date):
        os.mkdir(curr_date)
    os.chdir(curr_date)
    curr_time = date.strftime('%H-%M-%S')

    if not os.path.exists(curr_time):
        os.mkdir(curr_time)
    os.chdir(curr_time)
    analytical_data_dir_name = "analytical_data"
    figures_dir_name = "figures"
    frames_dir_name = "frames"
    os.mkdir(analytical_data_dir_name)
    os.mkdir(figures_dir_name)
    os.mkdir(frames_dir_name)
    new_output_dirs_dict["output_dir"] = outputs_dir
    new_output_dirs_dict["username_dir"] = outputs_dir + "/" + username
    new_output_dirs_dict["output_movie_dir"] = outputs_dir + "/" + username + "/" + video_name
    new_output_dirs_dict["date_path"] = outputs_dir + "/" + username + "/" + video_name + "/" + curr_date
    new_output_dirs_dict[
        "time_path"] = outputs_dir + "/" + username + "/" + video_name + "/" + curr_date + "/" + curr_time
    new_output_dirs_dict[
        "analytical_data_path"] = outputs_dir + "/" + username + "/" + video_name + "/" + curr_date + "/" + curr_time + "/" + analytical_data_dir_name
    new_output_dirs_dict[
        "figures_path"] = outputs_dir + "/" + username + "/" + video_name + "/" + curr_date + "/" + curr_time + "/" + figures_dir_name
    new_output_dirs_dict[
        "frames_path"] = outputs_dir + "/" + username + "/" + video_name + "/" + curr_date + "/" + curr_time + "/" + frames_dir_name
    new_output_dirs_dict[
        'annotated_video'] = outputs_dir + "/" + username + "/" + video_name + "/" + curr_date + "/" + curr_time + "/" + "annotated_video.mp4"
    os.chdir(get_src_path())
    global output_dirs_dict
    output_dirs_dict = new_output_dirs_dict


def zip_output():
    filename = get_file_name_for_backslash(output_dirs_dict['output_movie_dir'])
    zip_out_path = output_dirs_dict['username_dir']
    folder_to_compress = output_dirs_dict['time_path']
    time = output_dirs_dict['time_path'].split('/')[-1]
    date = output_dirs_dict['date_path'].split('/')[-1]
    zip_name = '{}_{}_{}.zip'.format(filename, date, time)
    make_archive(folder_to_compress, zip_out_path, zip_name)
    return zip_out_path + '/{}'.format(zip_name)


def make_archive(source, destination, zip_name):
    destination += "/" + zip_name
    base_name = '.'.join(destination.split('.')[:-1])
    format = zip_name.split('.')[-1]
    root_dir = os.path.dirname(source)
    base_dir1 = os.path.basename(source.strip(os.sep))
    shutil.make_archive(base_name, format, root_dir, base_dir1)


def delete_generate_dirs():
    shutil.rmtree(output_dirs_dict['output_movie_dir'])


def send_zip(src_zip, dest_path, delete_output_folder=False):
    print('begin to send zip')
    shutil.move(src_zip, dest_path)
    print('moved zip')
    if delete_output_folder:
        delete_generate_dirs()
        print('deleted generate dirs')


def get_output_dirs_dict():
    return output_dirs_dict


def get_expected_output_dirs_dict():
    return expected_output_dirs_dict


def get_analytics_dir():
    return output_dirs_dict['analytical_data_path']


def get_figures_dir():
    return output_dirs_dict['figures_path']


def analytical_df_to_csv(df, filename):
    analytical_dir_path = output_dirs_dict['analytical_data_path']
    outp_path = analytical_dir_path + '/' + filename
    pd.DataFrame.to_csv(df, outp_path, index=False)
    return outp_path


def get_output_dir_path(key=None):
    if key is None:
        return output_dirs_dict
    return output_dirs_dict[key]


def get_excepted_data_path():
    return "../excepted_data"


def get_excepted_csvs_path():
    return get_excepted_data_path() + "/csvs"


def get_excepted_videos_path():
    return get_excepted_data_path() + "/videos"


def get_excepted_csv_path_for_movie(video_full_name):
    video_name = video_full_name.split('_from')[0]
    all_excepted_csvs_path = get_excepted_csvs_path()
    wanted_path = all_excepted_csvs_path + '/' + video_name + '_expected.csv'
    return wanted_path if os.path.exists(wanted_path) else None
