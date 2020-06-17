import os


def path_without_suffix(path):
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


def get_file_name(path):
    return path.split('/')[-1]


def get_file_name_for_backslash(path):
    return path.split('/')[-1]


def get_number_of_start_frame(movie_name):
    name_parts = movie_name.split('_')
    return int(name_parts[-1])


def get_src_path():
    return os.path.dirname(os.path.realpath(__file__))


def get_plug_and_play_functions_dir():
    return os.getcwd() + '/../plug_and_play_functions'


def get_body_parts_columns():
    return ['NoseX', 'NoseY', 'NoseScore', 'NeckX', 'NeckY', 'NeckScore', 'RShoulderX', 'RShoulderY',
            'RShoulderScore', 'RElbowX', 'RElbowY', 'RElbowScore', 'RWristX', 'RWristY', 'RWristScore', 'LShoulderX',
            'LShoulderY', 'LShoulderScore',
            'LElbowX', 'LElbowY', 'LElbowScore', 'LWristX', 'LWristY', 'LWristScore']


def get_body_parts():
    return ['Nose', 'Neck', 'RShoulder', 'RElbow', 'RWrist', 'LShoulder', 'LElbow', 'LWrist']


def get_body_skeleton():
    return [[0, 1], [1, 2], [1, 5], [2, 3], [3, 4], [5, 6], [6, 7]]


def keypoint_to_score(col_name):
    if col_name[-1] == 'X' or col_name[-1] == 'Y':
        return col_name[:-1] + 'Score'
    elif 'Score' in col_name:
        return col_name
    return col_name + 'Score'


if __name__ == "__main__":
    print(get_src_path())
