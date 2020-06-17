import os
import shutil
from datetime import datetime
import utils
import pandas as pd
from utils import get_src_path, get_file_name_for_backslash

expected_output_dirs_dict = {}
output_dirs_dict = {}


def generate_dirs_for_output_of_movie(movie_name, username='guest'):
    """ Generates a directory per movie, user, and upload time.
        The hierarchy is Output Directory/Username/Upload Date/Upload Time
        The paths are keeped in output_dirs_dict (Dictionary)

    :param movie_name:
    :param username:
    """
    video_name = utils.path_without_suffix(movie_name)
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
    swimfix_frames_dir_name = "swimfix_annotated_frames"
    os.mkdir(analytical_data_dir_name)
    os.mkdir(figures_dir_name)
    os.mkdir(frames_dir_name)
    os.mkdir(swimfix_frames_dir_name)
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
        "swimfix_frames_path"] = outputs_dir + "/" + username + "/" + video_name + "/" + curr_date + "/" + curr_time + "/" + swimfix_frames_dir_name
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


def get_output_dirs_dict():
    return output_dirs_dict


def get_expected_output_dirs_dict():
    return expected_output_dirs_dict


def get_analytics_dir():
    return output_dirs_dict['analytical_data_path']


def get_figures_dir():
    return output_dirs_dict['figures_path']


def analytical_df_to_csv(df, filename, output_path=None):
    analytical_dir_path = output_dirs_dict['analytical_data_path'] if output_path is None else output_path
    outp_path = analytical_dir_path + '/' + filename
    pd.DataFrame.to_csv(df, outp_path, index=False)
    return outp_path


def get_output_dir_path(key=None):
    if key is None:
        return output_dirs_dict
    return output_dirs_dict[key]


def get_expected_data_path():
    return "../expected_data"


def get_expected_csvs_path():
    return get_expected_data_path() + "/csvs"


def get_expected_videos_path():
    return get_expected_data_path() + "/videos"


def get_expected_csv_path_for_movie(video_full_name):
    """Checks if there is an expected csv file in server and returns the path to this file. Otherwise, returns None"""
    video_name = video_full_name.split('_from')[0]
    all_expected_csvs_path = get_expected_csvs_path()
    wanted_path = all_expected_csvs_path + '/' + video_name + '_expected.csv'
    return wanted_path if os.path.exists(wanted_path) else None


def get_expected_output_dirs_dict():
    return expected_output_dirs_dict


def build_test_environment_dir(filename, username='guest'):
    """ Build test environment for specific movie with the filename specified.
        The environment will include:
        - Ground_truth : csv files with information derived from Server/expected_data/csvs/<filename>_expected
        - Frames : Frame with annotations for this movie.
        - Test Results: Directory with csv files for comparison between OpenPose results to the ground truth.

    :param filename: Movie name.
    :return: Triplet with paths to all directories the environment includes.
    """
    test_dir = '../tests'
    if not os.path.exists(test_dir):
        os.mkdir(test_dir)

    #username
    username_test_dir = test_dir + '/' + username
    if not os.path.exists(username_test_dir):
        os.mkdir(username_test_dir)

    # movie
    movie_test_env_dir = username_test_dir + '/' + filename
    if not os.path.exists(movie_test_env_dir):
        os.mkdir(movie_test_env_dir)

    # hour
    date = datetime.now()
    curr_date = date.strftime('%Y-%m-%d')
    date_path = movie_test_env_dir + '/' + curr_date
    if not os.path.exists(date_path):
        os.mkdir(date_path)

    # time
    curr_time = date.strftime('%H-%M-%S')
    time_path = date_path + '/' + curr_time
    if not os.path.exists(time_path):
        os.mkdir(time_path)

    # data
    movie_ground_truth_data_dir = time_path + '/ground_truth_data'
    if not os.path.exists(movie_ground_truth_data_dir):
        os.mkdir(movie_ground_truth_data_dir)

    movie_frames_dir = time_path + '/frames'
    if not os.path.exists(movie_frames_dir):
        os.mkdir(movie_frames_dir)

    movie_test_results_dir = time_path + '/test_results'
    if not os.path.exists(movie_test_results_dir):
        os.mkdir(movie_test_results_dir)

    new_expected_output_dict = dict()
    new_expected_output_dict['test_results_path'] = movie_test_results_dir
    new_expected_output_dict['frames_path'] = movie_frames_dir
    new_expected_output_dict['ground_truth_data_path'] = movie_ground_truth_data_dir
    new_expected_output_dict['time_path'] = time_path
    new_expected_output_dict['date_path'] = date_path
    new_expected_output_dict['movie_test_env_path'] = movie_test_env_dir
    new_expected_output_dict['tests_path'] = test_dir
    global expected_output_dirs_dict
    expected_output_dirs_dict = new_expected_output_dict

    return movie_frames_dir, movie_ground_truth_data_dir, movie_test_results_dir


def generate_data_folders():
    os.chdir('..')
    if not os.path.exists('expected_data'):
        os.mkdir('expected_data')
    if not os.path.exists('temp'):
        os.mkdir('temp')
    if not os.path.exists('tests'):
        os.mkdir('tests')
    if not os.path.exists('videos'):
        os.mkdir('videos')
    if not os.path.exists('plug_and_play_functions'):
        os.mkdir('plug_and_play_functions')
    os.chdir('expected_data')
    if not os.path.exists('csvs'):
        os.mkdir('csvs')
    os.chdir(get_src_path())
