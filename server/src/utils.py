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


def get_id_of_file(path):
    filename = path_without_suffix(path.split('/')[-1])
    id = filename.split('_')[-1]
    return id


def get_file_name(path):
    return path.split('/')[-1]


def get_file_name_for_backslash(path):
    return path.split('/')[-1]


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


def keypoint_to_score(col_name):
    if col_name[-1] == 'X' or col_name[-1] == 'Y':
        return col_name[:-1] + 'Score'
    elif 'Score' in col_name:
        return col_name
    return col_name + 'Score'


if __name__ == "__main__":
    print(get_src_path())
