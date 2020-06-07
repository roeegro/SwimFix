# Edited by Roee Groiser and Tom Marzea
import math
import cv2
import numpy as np
from scipy import interpolate
import output_manager
import utils
import pandas as pd

from main import *


def generate_vectors_csv(csv_path, filename='vectors.csv', output_path=None):
    """ Generates csv file with vectors from csv file contains all key points derived earlier.

    :param csv_path: path to csv file contains all key points information derived before using this function.
    :param filename: file name of generated file.
    :param output_path: path to generated csv file to be located in.
    :return: path to generated csv file to be located in.
    """
    df = pd.read_csv(csv_path)
    df.reset_index(drop=True, inplace=True)
    vectors_df = pd.DataFrame(
        columns=['Frame Number', 'RChestX', 'RChestY', 'LChestX', 'LChestY', 'RArmX', 'RArmY', 'LArmX', 'LArmY',
                 'RForearmX', 'RForearmY', 'LForearmX', 'LForearmY'])
    kp_cols = sorted(filter(lambda name: 'Score' not in name, df.columns.values))
    df.drop(columns=df.columns.difference(kp_cols), axis=1, inplace=True)
    df.reset_index(drop=True, inplace=True)
    # frame_nums = df['Frame Number'].values
    # df.insert(0, 'Frame Number', frame_nums)
    # kp_cols.remove('Frame Number')
    for idx, frame in df.iterrows():
        frame_vectors = {'Frame Number': frame['Frame Number'],
                         'RChestX': frame['RShoulderX'] - frame['NeckX'],
                         'RChestY': frame['RShoulderY'] - frame['NeckY'],
                         'LChestX': frame['LShoulderX'] - frame['NeckX'],
                         'LChestY': frame['LShoulderY'] - frame['NeckY'],
                         'RArmX': frame['RShoulderX'] - frame['RElbowX'],
                         'RArmY': frame['RShoulderY'] - frame['RElbowY'],
                         'LArmX': frame['LShoulderX'] - frame['LElbowX'],
                         'LArmY': frame['LShoulderY'] - frame['LElbowY'],
                         'RForearmX': frame['RElbowX'] - frame['RWristX'],
                         'RForearmY': frame['RElbowY'] - frame['RWristY'],
                         'LForearmX': frame['LElbowX'] - frame['LWristX'],
                         'LForearmY': frame['LElbowY'] - frame['LWristY'], }
        vectors_df = vectors_df.append(frame_vectors, ignore_index=True)
    outp_path = output_manager.get_analytics_dir() + '/' + filename if output_path is None else output_path + '/' + filename
    pd.DataFrame.to_csv(vectors_df, outp_path, index=False)
    return outp_path


def dotproduct(v1, v2):
    """ Returns the dot product of 2 vectors.  """
    return sum((a * b) for a, b in zip(v1, v2))


def length(v):
    """ Returns the normal of vector.  """
    return math.sqrt(dotproduct(v, v))


def angle(v1, v2):
    return math.degrees(math.acos(dotproduct(v1, v2) / (length(v1) * length(v2))))


def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)


def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return math.degrees(np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)))
    # return np.arccos(np.dot(v1_u, v2_u))


def generate_angles_csv(csv_path, filename='angles.csv', output_path=None, max_distance=10,
                        min_length=3):
    """ Generates a csv file contains relevant angles for swimmers, derived from csv_path contains vectors.

    :param csv_path:  a path to csv that contains vectors.
    :param filename: file name of the generated csv.
    :param output_path: path to generated csv.
    :return: path to generated csv.
    """
    vectors_df = pd.read_csv(csv_path)
    angles_df = pd.DataFrame(columns=['Frame Number', 'RShoulderAng', 'LShoulderAng', 'RElbowAng', 'LElbowAng'])
    for idx, frame in vectors_df.iterrows():
        RChestVec = (frame['RChestX'], frame['RChestY'])
        LChestVec = (frame['LChestX'], frame['LChestY'])
        RArmVec = (frame['RArmX'], frame['RArmY'])
        LArmVec = (frame['LArmX'], frame['LArmY'])
        RForearmVec = (frame['RForearmX'], frame['RForearmY'])
        LForearmVec = (frame['LForearmX'], frame['LForearmY'])
        neg = tuple([-1 * x for x in RChestVec])
        frame_angels = {'Frame Number': frame['Frame Number'],
                        'RShoulderAng': angle(tuple([x for x in RChestVec]), RArmVec),
                        'LShoulderAng': angle(tuple([x for x in LChestVec]), LArmVec),
                        'RElbowAng': angle(tuple([-1 * x for x in RArmVec]), RForearmVec),
                        'LElbowAng': angle(tuple([-1 * x for x in LArmVec]), LForearmVec),
                        }
        angles_df = angles_df.append(frame_angels, ignore_index=True)

    for column in angles_df.columns[1:]:
        counter = 0
        start_interval = angles_df.index.min()
        interval_list_per_this_column = list()
        # Find intervals
        for index in angles_df.index:
            if math.isnan(angles_df[column][index]):
                if counter >= min_length:
                    interval_list_per_this_column.append({'start': int(start_interval), 'end': int(index)})
                start_interval = index + 1
                counter = 0
            else:
                counter += 1
        # Merge between intervals
        for interval_index in range(len(interval_list_per_this_column) - 1):
            start_seond_interval = interval_list_per_this_column[interval_index + 1]['start']
            # start_first_interval = interval_list_per_this_column[interval_index]['start']
            end_first_interval = interval_list_per_this_column[interval_index]['end']
            # end_second_interval = interval_list_per_this_column[interval_index + 1]['end']
            if start_seond_interval - end_first_interval <= max_distance:
                frames_to_interpolate = np.arange(end_first_interval + 1, start_seond_interval)
                try:
                    angles_df.loc[frames_to_interpolate, [column]] = np.nan
                except:
                    continue  # for some perfect intervals which we don't have to fix.
                interval_df = angles_df.loc[end_first_interval - 2:start_seond_interval + 2, [column]]
                interval_df[column].interpolate(method='cubic', inplace=True)
                angles_df.loc[end_first_interval - 2:start_seond_interval + 2, [column]] = interval_df

    outp_path = output_manager.analytical_df_to_csv(angles_df, filename, output_path=output_path)
    # pd.DataFrame.to_csv(angles_df, filname, index=False)
    return outp_path


def generate_detected_keypoints_csv(csv_path, score_cols=None, filename=None, output_path=None):
    df = pd.read_csv(csv_path)
    if score_cols is None:
        if filename is None:
            filename = 'detected_keypoints.csv'
        score_cols = list(filter(lambda x: 'Score' in x, df.columns.values))[1:]
    else:
        if filename is None:
            filename = 'is_' + '_'.join(score_cols) + 'detected.csv'
        score_cols = list(map(utils.keypoint_to_score, score_cols))
    is_detected_cols = list(map(lambda x: x.replace('Score', ''), score_cols))
    path = output_manager.get_analytics_dir() + '/' + filename if output_path is None else output_path + '/' + filename
    is_detected_df = pd.DataFrame(columns=['Frame Number'] + is_detected_cols)
    for idx, frame in df.iterrows():
        is_detected_frame = {'Frame Number': frame['Frame Number']}
        for score_col in score_cols:
            is_detected_col = score_col.replace('Score', '')
            if math.isnan(frame[score_col]):
                is_detected_frame[is_detected_col] = 0
            else:
                is_detected_frame[is_detected_col] = 1
        is_detected_df = is_detected_df.append(is_detected_frame, ignore_index=True)
    is_detected_df.reset_index(drop=True, inplace=True)
    pd.DataFrame.to_csv(is_detected_df, path, index=False)
    return path


def generate_interpolated_csv(csv_path, y_cols=None, x_col='Frame Number', filename=None, output_path=None):
    """ Generates csv file contains all key points given in csv_path after interpolation of coordinates values.

    :param csv_path: a path to csv contains all key points coordinates.
    :param y_cols: columns of key points coordinates to be interpolated.
    :param x_col: column from csv_path to be the index of the generated csv.
    :param filename: file name for the generated csv file.
    :param output_path: path to generate csv file to.
    :return: path to the generated csv file.
    """
    df = pd.read_csv(csv_path)
    if output_path is None:
        output_path = output_manager.get_analytics_dir()
    if y_cols is None:
        cols = list(filter(lambda name: 'Score' not in name, df.columns.values))
        y_cols = cols.copy()
        y_cols.remove(x_col)
        path = output_path + '/interpolated_' + utils.path_without_suffix(utils.get_file_name(csv_path)) + '.csv'
    elif type(y_cols) == str:
        y_cols = [y_cols]
        cols = y_cols + [x_col]
        path = output_path + '/' + '_'.join(y_cols) + '.csv'
    else:
        cols = y_cols + [x_col]
        path = output_path + '/' + '_'.join(y_cols) + '.csv'
    if filename is not None:
        path = output_path + '/' + filename + '.csv'
    df.drop(columns=df.columns.difference(cols), axis=1, inplace=True)
    for col_name in y_cols:
        first_notna_frame = df[col_name].notna().idxmax()
        last_notna_frame = df[col_name].notna()[::-1].idxmax()
        df = df.iloc[first_notna_frame:last_notna_frame + 1]
        df.reset_index(drop=True, inplace=True)
        df.set_index(['Frame Number'])
        df = df[df.columns.dropna()]
        df[col_name].interpolate(method='cubic', inplace=True)
        y = df[col_name].values
        x = df['Frame Number'].values
        xnew = np.linspace(x.min(), x.max(), len(x))
        bspline = interpolate.make_interp_spline(x, y)
        y_smoothed = bspline(xnew)
        df[col_name] = y_smoothed

    df.to_csv(path, index=False)
    return path


body_parts = utils.get_body_parts()  # all body parts to be used in our analysis.


def get_keypoints_csv_from_video(video_path, params):
    """ Generates csv files contains information about key points, derived from video located in video_path.
        Key points detection is done by OpenPose library using configurations defined in params.
        The function also generates video with annotation of OpenPose and frames of this video.
        All those outputs are located in Server/output/<username>/<current date>/<current time>

    :param video_path: path to video to be extracted key points from.
    :param params: Dictionary contains OpenPose configurations.
    :return: path to csv file that contains all key points extracted from video using OpenPose.
    """
    video_name = utils.get_file_name(video_path)
    video_name = utils.path_without_suffix(video_name)
    output_dirs = output_manager.get_output_dirs_dict()  # must be created before calling to this function.
    size = (600, 480)
    annotated_video_cap = cv2.VideoWriter('annotated_video.avi', cv2.VideoWriter_fourcc(*'MP4V'), 30, size)

    # Starting OpenPose
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()

    # Process Image
    datum = op.Datum()
    print("path is {}".format(video_path))
    cap = cv2.VideoCapture(video_path)
    valid_frames_df = pd.DataFrame(columns=['Frame Number'] + body_parts)
    invalid_frames_df = pd.DataFrame(columns=['Frame Number'] + body_parts)
    all_keypoints_df = pd.DataFrame(columns=['Frame Number'] + body_parts)
    frame_detected_df = pd.DataFrame(columns=['Frame Number', 'Detected'])
    frame_counter = utils.get_number_of_start_frame(video_name)

    while cap.isOpened():
        check, frame = cap.read()
        if not check:
            break
        resized_frame = cv2.resize(frame, (600, 480), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
        # emplace keypoints
        datum.cvInputData = resized_frame
        opWrapper.emplaceAndPop([datum])
        detected_keypoints = datum.poseKeypoints
        annotated_frame = datum.cvOutputData
        annotated_video_cap.write(annotated_frame)
        cv2.imshow('Annotated frame', annotated_frame)
        cv2.imwrite(output_dirs['frames_path'] + "/annotated_frame_{}.jpg".format(frame_counter), annotated_frame)
        # Extracting points coordinates into csv file
        if not datum.poseKeypoints.shape == ():
            first_person_keypoints = detected_keypoints[0]
            current_frame_keypoints = np.array([frame_counter])
            # make representation of each relevant point
            for i, body_part in enumerate(first_person_keypoints):
                if i < len(body_parts) / 3:  # take only 8 first points which are relevant to our detection
                    xCoor = body_part[0] if body_part[0] != 0 else math.nan
                    yCoor = body_part[1] if body_part[1] != 0 else math.nan
                    score = body_part[2] if body_part[2] != 0 else math.nan
                    body_part_keypoints = np.array([xCoor, yCoor, score])  # specific keypoint
                    # concat to the keypoints detected in this frame
                    current_frame_keypoints = np.append(current_frame_keypoints, body_part_keypoints)

            current_frame_keypoints_df = pd.DataFrame(columns=['Frame Number'] + body_parts,
                                                      data=[current_frame_keypoints])
            all_keypoints_df = pd.concat([all_keypoints_df, current_frame_keypoints_df], sort=False)
            if valid_frame(current_frame_keypoints_df.loc[:, 'NeckX':]):
                # if True:
                valid_frames_df = pd.concat([valid_frames_df, current_frame_keypoints_df], sort=False)
                frame_detected_df = pd.concat([frame_detected_df, pd.DataFrame(data=[[frame_counter, 1]])])
            else:
                invalid_frames_df = pd.concat(
                    [invalid_frames_df, pd.DataFrame(columns=['Frame Number'] + body_parts, data=[[frame_counter] +
                                                                                                  ([np.nan] * len(
                                                                                                      body_parts))])],
                    sort=False)
                frame_detected_df = pd.concat([frame_detected_df, pd.DataFrame(data=[[frame_counter, 0]])])
        else:
            all_keypoints_df = pd.concat(
                [all_keypoints_df, pd.DataFrame(columns=['Frame Number'] + body_parts, data=[[frame_counter] +
                                                                                             ([np.nan] * len(
                                                                                                 body_parts))])],
                sort=False)
            invalid_frames_df = pd.concat(
                [invalid_frames_df, pd.DataFrame(columns=['Frame Number'] + body_parts, data=[[frame_counter] +
                                                                                              ([np.nan] * len(
                                                                                                  body_parts))])],
                sort=False)
            frame_detected_df = pd.concat(
                [frame_detected_df, pd.DataFrame(columns=['Frame Number', 'Detected'], data=[[frame_counter, 0]])],
                sort=False)

        frame_counter += 1
        key = cv2.waitKey(1)

    # When everything done, release
    # the video capture object
    print("finished")
    cap.release()
    annotated_video_cap.release()
    shutil.move('annotated_video.avi', output_dirs['annotated_video'])
    valid_frames_df.to_csv(output_dirs['analytical_data_path'] + "/valid_keypoints.csv", index=False)
    invalid_frames_df.to_csv(output_dirs['analytical_data_path'] + "/invalid_keypoints.csv", index=False)
    frame_detected_df.to_csv(output_dirs['analytical_data_path'] + "/is_frame_detected.csv", index=False)
    all_keypoints_df.to_csv(output_dirs['analytical_data_path'] + "/all_keypoints.csv", index=False)
    # Closes all the frames
    cv2.destroyAllWindows()

    return output_dirs['analytical_data_path'] + "/all_keypoints.csv"


def valid_frame(current_frame_df):
    """ Checks if frame contains enough information to be included in 'valid_keypoints.csv'

    :param current_frame_df: Pandas DataFrame contains row of key points extracted in some frame.
    :return: True if frame contains enough information to be included in 'valid_keypoints.csv'. Otherwise-  False.
    """
    number_of_detected_body_parts = 0
    frame = current_frame_df.iloc[0]
    neck_detected = (not (float)(frame[0]) == 0.) and (not (float)(frame[1]) == 0.)
    number_of_body_parts = (int)(len(frame) / 3)
    for i in range(number_of_body_parts):
        if (not math.isnan((float)((frame[3 * i])))) or (not math.isnan((float)((frame[(3 * i) + 1])))):
            number_of_detected_body_parts += 1
    if number_of_detected_body_parts > 0.75 * number_of_body_parts or (
            number_of_detected_body_parts > number_of_body_parts * 0.6 and neck_detected):
        return True
    return False


def filter_and_interpolate(csv_path, y_cols=None, x_col='Frame Number', filename=None, output_path=None,
                           min_interval_length=3, score_threshold=0.4):
    """ Gets path to csv file contains all key points in 'get_keypoints_csv_from_video'.
        The function takes this file, build intervals for neck,nose,right side and left side with 'min_interval_length'
        length contains key points with scores higher than 'score_threshold', extend each interval and merge between
        some intervals, and filter key points coordinates which are not in some intervals.

    :param csv_path: All key points csv path.
    :param y_cols:
    :param x_col: Index of input and output of csv path.
    :param filename: File name of the generated csv file after the process.
    :param output_path: Path of the generated csv file after the process.
    :param min_interval_length: Minimum initial intervals length for some body part.
    :param score_threshold: Minimum confidence score of some key point to be located in the interval.
    :return: Path of the generated csv file after the process.
    """
    df = pd.read_csv(csv_path)
    if output_path is None:
        output_path = output_manager.get_analytics_dir()
    if y_cols is None:
        cols = list(filter(lambda name: 'Score' not in name, df.columns.values))
        y_cols = cols.copy()
        y_cols.remove(x_col)
        path = output_path + '/interpolated_and_filtered_' + utils.path_without_suffix(
            utils.get_file_name(csv_path)) + '.csv'
    elif type(y_cols) == str:
        y_cols = [y_cols]
        cols = y_cols + [x_col]
        path = output_path + '/' + '_'.join(y_cols) + '.csv'
    else:
        cols = y_cols + [x_col]
        path = output_path + '/' + '_'.join(y_cols) + '.csv'
    if filename is not None:
        path = output_path + '/' + filename + '.csv'

    df['Frame Number'].astype('int64')
    df = df.set_index('Frame Number')

    df_to_show = df.drop(columns=df.columns.difference(cols), axis=1)
    sides = ['L', 'R']
    intervals_list = list()
    intervals_per_side = dict()
    for side in sides:
        interval_list_per_hand = get_relevant_intervals_for_hand(df, side,
                                                                 min_interval_length, score_threshold)
        # extended_interval_list_per_hand = try_extend_intervals_by_side(df, interval_list_per_hand, side)
        merged_interval_list_per_hand = try_merge_between_intervals(interval_list_per_hand)
        # intervals_per_side[side] = merged_interval_list_per_hand
        side_cols = list(filter(lambda name: name.startswith(side) and not "Shoulder" in name, y_cols))
        for interval in merged_interval_list_per_hand:
            intervals_list.append(interval)
            start_interval_frame = int(interval['start'])
            end_interval_frame = int(interval['end'])
            interval_df = df.loc[start_interval_frame:end_interval_frame, side_cols]
            try:
                interval_df.loc[interval['frames_to_inerpolate'], interval_df.columns] = np.nan
            except:
                continue  # for some perfect intervals which we don't have to fix.
            for col_name in side_cols:
                interval_df[col_name].interpolate(method='cubic', inplace=True)
                df_to_show.loc[interval['frames_to_inerpolate'], col_name] = interval_df.loc[
                    interval['frames_to_inerpolate'], col_name]  # update df
        intervals_per_side[side] = try_extend_intervals_by_side(df, merged_interval_list_per_hand, side)

    filter_frames_without_reliable_info_for_sides(df_to_show, intervals_per_side, sides)

    intervals_per_body_part = dict()
    for body_part in ['Nose', 'Neck', 'LShoulder', 'RShoulder']:
        interval_list_per_body_part = get_relevant_intervals_for_body_part(df, body_part, min_interval_length,
                                                                           score_threshold)
        # extended_interval_list_body_part = try_extend_intervals_by_body_part(df, interval_list_per_body_part, body_part)
        merged_interval_list_per_body_part = try_merge_between_intervals(interval_list_per_body_part)
        body_cols = list(filter(lambda name: name.startswith(body_part), y_cols))
        # intervals_per_body_part[body_part] = merged_interval_list_per_body_part
        for interval in merged_interval_list_per_body_part:
            intervals_list.append(interval)
            start_interval_frame = int(interval['start'])
            end_interval_frame = int(interval['end'])
            interval_df = df.loc[start_interval_frame:end_interval_frame, body_cols]
            try:
                interval_df.loc[interval['frames_to_inerpolate'], interval_df.columns] = np.nan
            except:
                continue  # for some perfect intervals which we don't have to fix.
            for col_name in body_cols:
                interval_df[col_name].interpolate(method='cubic', inplace=True)
                df_to_show.loc[interval['frames_to_inerpolate'], col_name] = interval_df.loc[
                    interval['frames_to_inerpolate'], col_name]  # update df
        intervals_per_body_part[body_part] = try_extend_intervals_by_body_part(df, merged_interval_list_per_body_part,
                                                                               body_part)
    filter_frames_without_reliable_info(df_to_show, intervals_per_body_part, ['Nose', 'Neck'])
    filter_frames_without_reliable_info(df_to_show, intervals_per_body_part, ['LShoulder', 'RShoulder'])

    neck_estimator(df_to_show, intervals_per_body_part)
    df_to_show.to_csv(path)
    return path


def neck_estimator(df, intervals_per_body_part):
    # step 1: use mean shoulders rule if necessary
    for index, frame in df.iterrows():
        if not math.isnan(df['NeckX'][index]):  # we already know neck location
            continue
        elif not math.isnan(df['LShoulderX'][index]) and not math.isnan(df['RShoulderX'][index]):
            df['NeckX'][index] = (df['LShoulderX'][index] + df['RShoulderX'][index]) / 2
            df['NeckY'][index] = (df['LShoulderY'][index] + df['RShoulderY'][index]) / 2
    # after calculation of mean shoulders exhaustively, we want to take
    # average location of each shoulder and neck and try to use the distance of one shoulder from mean location.
    for interval in intervals_per_body_part['LShoulder']:
        interval_df = df.loc[interval['start']:interval['end'], :]
        mean_l_shoulder_x = interval_df['LShoulderX'].mean()
        mean_l_shoulder_y = interval_df['LShoulderY'].mean()
        mean_neck_x = interval_df['NeckX'].mean()
        mean_neck_y = interval_df['NeckY'].mean()
        for index, frame in interval_df.iterrows():
            if math.isnan(interval_df['NeckX'][index]):
                if not math.isnan(df['LShoulderX'][index]) and math.isnan(
                        df['RShoulderX'][index]):  # Only left shoulder is known
                    epsilon_x = mean_l_shoulder_x - df['LShoulderX'][index]
                    epsilon_y = mean_l_shoulder_y - df['LShoulderY'][index]
                    df['NeckX'][index] = mean_neck_x + (epsilon_x / 2)
                    df['NeckY'][index] = mean_neck_y + (epsilon_y / 2)
                else:
                    continue
            else:
                continue
    for interval in intervals_per_body_part['RShoulder']:
        interval_df = df.loc[interval['start']:interval['end'], :]
        mean_r_shoulder_x = interval_df['RShoulderX'].mean()
        mean_r_shoulder_y = interval_df['RShoulderY'].mean()
        mean_neck_x = interval_df['NeckX'].mean()
        mean_neck_y = interval_df['NeckY'].mean()
        for index, frame in interval_df.iterrows():
            if math.isnan(interval_df['NeckX'][index]):
                if math.isnan(df['LShoulderX'][index]) and not math.isnan(
                        df['RShoulderX'][index]):  # Only right shoulder is known
                    epsilon_x = mean_r_shoulder_x - df['RShoulderX'][index]
                    epsilon_y = mean_r_shoulder_y - df['RShoulderY'][index]
                    df['NeckX'][index] = mean_neck_x + (epsilon_x / 2)
                    df['NeckY'][index] = mean_neck_y + (epsilon_y / 2)
                else:
                    continue
            else:
                continue


def try_extend_intervals_by_side(df, interval_list_per_hand, side):
    """ Tries to extend intervals. For each interval, calculates the average distance of wrist Y coordinate
        over frames in interval. Then, the function looks for frames next and before the interval that
        change is smaller than avg. change and upward trend is identical to upward trend in the frames
        key points inside the interval.

    :param df: Pandas Dataframe of all key points derived from path given in 'filter_and_interpolate'.
    :param interval_list_per_hand: list of initial intervals per hand from some side
    :param side: 'L' - left hand side , 'R' - right hand side
    :return: List with extended intervals.
    """
    extended_interval_list_per_hand = list()
    relevant_body_parts = list(filter(lambda name: name.startswith(side), df.columns))
    for interval in interval_list_per_hand:
        start_interval_frame = int(interval['start'])
        new_start_interval_frame = start_interval_frame
        end_interval_frame = int(interval['end'])
        new_end_interval_frame = end_interval_frame
        interval_df = df.loc[start_interval_frame:end_interval_frame, relevant_body_parts]

        # calculate avg distance
        avg_distance = 0
        for index, row in interval_df.iterrows():
            if index == start_interval_frame:
                continue
            avg_distance += math.fabs(
                float(interval_df[side + 'WristY'][index]) - float(interval_df[side + 'WristY'][index - 1]))
        avg_distance = avg_distance / (len(interval_df) - 1)
        # Look forward
        forward_upward_trend = True if float(df[side + 'WristY'][end_interval_frame]) > float(
            df[side + 'WristY'][end_interval_frame - 1]) else False
        backward_upward_trend = True if float(df[side + 'WristY'][start_interval_frame + 1]) > float(
            df[side + 'WristY'][start_interval_frame]) else False

        try:
            while math.fabs(float(df[side + 'WristY'][new_end_interval_frame]) - float(
                    df[side + 'WristY'][new_end_interval_frame - 1])) < avg_distance and \
                    float(df[side + 'WristY'][new_end_interval_frame]) > float(
                df[side + 'WristY'][new_end_interval_frame - 1]) is forward_upward_trend:
                new_end_interval_frame += 1
        except:
            new_end_interval_frame -= 1  # because we get out of bounds of df

        # Look backward
        try:
            while math.fabs(float(df[side + 'WristY'][new_start_interval_frame]) - float(
                    df[side + 'WristY'][new_start_interval_frame + 1])) < avg_distance and \
                    (float(df[side + 'WristY'][new_start_interval_frame + 1]) - float(
                        df[side + 'WristY'][new_start_interval_frame]) > 0) is backward_upward_trend:
                new_start_interval_frame -= 1
        except:
            new_start_interval_frame += 1  # because we get out of bounds of df

        extended_interval_list_per_hand.append({'start': new_start_interval_frame, 'end': new_end_interval_frame})
    return extended_interval_list_per_hand


def try_extend_intervals_by_body_part(df, interval_list_per_hand, body_part):
    """ Similar to 'try_extend_intervals_by_side' but does the same for specific body_part"""
    extended_interval_list_per_hand = list()
    relevant_body_parts = list(filter(lambda name: name.startswith(body_part), df.columns))
    for interval in interval_list_per_hand:
        start_interval_frame = int(interval['start'])
        new_start_interval_frame = start_interval_frame
        end_interval_frame = int(interval['end'])
        new_end_interval_frame = end_interval_frame
        interval_df = df.loc[start_interval_frame:end_interval_frame, relevant_body_parts]

        # calculate avg distance
        avg_distance = 0
        for index, row in interval_df.iterrows():
            if index == start_interval_frame:
                continue
            avg_distance += math.fabs(
                float(interval_df[body_part + 'Y'][index]) - float(interval_df[body_part + 'Y'][index - 1]))
        avg_distance = avg_distance / (len(interval_df) - 1)

        # Look forward
        forward_upward_trend = True if float(df[body_part + 'Y'][end_interval_frame]) - float(
            df[body_part + 'Y'][end_interval_frame - 1]) > 0 else False
        backward_upward_trend = True if float(df[body_part + 'Y'][start_interval_frame + 1]) - float(
            df[body_part + 'Y'][start_interval_frame]) > 0 else False
        try:
            while math.fabs(float(df[body_part + 'Y'][new_end_interval_frame]) - float(
                    df[body_part + 'Y'][new_end_interval_frame - 1])) < avg_distance and \
                    (float(df[body_part + 'Y'][new_end_interval_frame]) - float(
                        df[body_part + 'Y'][new_end_interval_frame - 1]) > 0) is forward_upward_trend:
                new_end_interval_frame += 1
        except:
            new_end_interval_frame -= 1  # because we get out of bounds of df
        frames_to_interpolate = np.arange(end_interval_frame + 1,
                                          new_end_interval_frame + 1)
        # Look backward
        try:
            while math.fabs(float(df[body_part + 'Y'][new_start_interval_frame]) - float(
                    df[body_part + 'Y'][new_start_interval_frame + 1])) < avg_distance and \
                    (float(df[body_part + 'Y'][new_start_interval_frame + 1]) - float(
                        df[body_part + 'Y'][new_start_interval_frame]) > 0) is backward_upward_trend:
                new_start_interval_frame -= 1
        except:
            new_start_interval_frame += 1  # because we get out of bounds of df

        extended_interval_list_per_hand.append({'start': new_start_interval_frame, 'end': new_end_interval_frame})
    return extended_interval_list_per_hand


def get_relevant_intervals_for_body_part(all_keypoints_df, body_part, min_interval_length, score_threshold):
    """ Goes over all_keypoints_df and build intervals s.t |interval| > min_interval_length, and
        foreach frame in interval: the score of body_part in frame is higher than score_threshold.

    :param all_keypoints_df: Pandas Dataframe of all key points derived from path given in 'filter_and_interpolate'.
    :param body_part: selected body_part to be build confident frames interval for.
    :param min_interval_length: Minimum length for frames interval.
    :param score_threshold: The score of body_part in frame is higher than score_threshold
    :return: Intervals list for body part as described above.
    """
    current_interval_len_counter = 0
    intervals_list_for_hand = list()
    start_interval_frame_number = all_keypoints_df.index.min()
    for index, row in all_keypoints_df.iterrows():
        if all_keypoints_df[body_part + 'Score'][index] > score_threshold:
            if current_interval_len_counter == 0:
                start_interval_frame_number = index
            current_interval_len_counter += 1
        elif current_interval_len_counter > min_interval_length:
            intervals_list_for_hand.append({'start': start_interval_frame_number, 'end': index - 1})
            start_interval_frame_number = index
            current_interval_len_counter = 0
        else:
            current_interval_len_counter = 0
    return intervals_list_for_hand


def get_relevant_intervals_for_hand(all_keypoints_df, side, min_interval_length, score_threshold):
    """ Similar to 'get_relevant_intervals_for_body_part' but does the same for some hand side."""
    current_interval_len_counter = 0
    intervals_list_for_hand = list()
    start_interval_frame_number = all_keypoints_df.index.min()
    for index, row in all_keypoints_df.iterrows():
        if all_keypoints_df[side + 'ElbowScore'][index] > score_threshold:
            if current_interval_len_counter == 0:
                start_interval_frame_number = index
            current_interval_len_counter += 1
        elif current_interval_len_counter > min_interval_length:
            intervals_list_for_hand.append({'start': start_interval_frame_number, 'end': index - 1})
            start_interval_frame_number = index
            current_interval_len_counter = 0
        else:
            current_interval_len_counter = 0
    return intervals_list_for_hand


def try_merge_between_intervals(interval_list, max_distance_between_intervals=10):
    """ Tries to merge between nearby intervals of same body part.

    :param interval_list: 
    :param max_distance_between_intervals: 
    :return: List of intervals (dictionaries) after merging.
    """
    merged_intervals_list_for_hand = list()
    merging = False
    start_frame = None
    frames_to_interpolate = []
    for index in range(len(interval_list)):
        if index == len(interval_list) - 1:
            if merging:
                frames_to_interpolate = np.append(frames_to_interpolate, np.arange(interval_list[index - 1]['end'] + 1,
                                                                                   interval_list[index]['start']))
                merged_intervals_list_for_hand.append({'start': start_frame, 'end': interval_list[index]['end'],
                                                       'frames_to_inerpolate': frames_to_interpolate})
                frames_to_interpolate = None
            else:
                merged_intervals_list_for_hand.append(interval_list[index])
        elif interval_list[index + 1]['start'] - interval_list[index][
            'end'] > max_distance_between_intervals:
            if not merging:
                merged_intervals_list_for_hand.append(interval_list[index])
            else:
                frames_to_interpolate = np.append(frames_to_interpolate, np.arange(interval_list[index - 1]['end'] + 1,
                                                                                   interval_list[index]['start']))
                merged_intervals_list_for_hand.append({'start': start_frame, 'end': interval_list[index]['end'],
                                                       'frames_to_inerpolate': frames_to_interpolate})
                frames_to_interpolate = None
                start_frame = None
                merging = False
        else:
            if merging:
                frames_to_interpolate = np.append(frames_to_interpolate, np.arange(interval_list[index - 1]['end'] + 1,
                                                                                   interval_list[index]['start']))
            else:
                start_frame = interval_list[index]['start']
                merging = True

    return merged_intervals_list_for_hand


def filter_frames_without_reliable_info_for_sides(df_to_show, intervals_per_side, two_keys_list):
    """ Gets pandas DataFrame df_to_show with all frames and keypoints and filters body parts
        records of frames that are not in some interval from interval list intervals_per_side.

    :param df_to_show: Pandas DataFrame which will be written to csv file. We will filter frames from this df.
    :param intervals_per_side: Intervals list.
    :param two_keys_list: Two body parts to filter by.
    """
    right_side_columns = list(
        filter(lambda name: name.startswith(two_keys_list[1]) and not "Shoulder" in name, df_to_show.columns))
    left_side_columns = list(
        filter(lambda name: name.startswith(two_keys_list[0]) and not "Shoulder" in name, df_to_show.columns))
    frames_out_of_wanted_ranges = df_to_show.index.tolist()
    reliable_intervals_for_right_side = intervals_per_side[two_keys_list[1]]
    reliable_intervals_for_left_side = intervals_per_side[two_keys_list[0]]
    for frame in frames_out_of_wanted_ranges:
        found_in_right = False
        found_in_left = False
        for interval in reliable_intervals_for_right_side:
            if frame in np.arange(interval['start'], interval['end'] + 1):
                found_in_right = True
                break
        for interval in reliable_intervals_for_left_side:
            if frame in np.arange(interval['start'], interval['end'] + 1):
                found_in_left = True
                break

        if not found_in_right:
            df_to_show.loc[[frame], right_side_columns] = np.nan
        if not found_in_left:
            df_to_show.loc[[frame], left_side_columns] = np.nan


def filter_frames_without_reliable_info(df_to_show, intervals_per_side, two_keys_list):
    """ Gets pandas DataFrame df_to_show with all frames and keypoints and filters body parts
        records of frames that are not in some interval from interval list intervals_per_side.

    :param df_to_show: Pandas DataFrame which will be written to csv file. We will filter frames from this df.
    :param intervals_per_side: Intervals list.
    :param two_keys_list: Two body parts to filter by.
    """
    right_side_columns = list(filter(lambda name: name.startswith(two_keys_list[1]), df_to_show.columns))
    left_side_columns = list(filter(lambda name: name.startswith(two_keys_list[0]), df_to_show.columns))
    frames_out_of_wanted_ranges = df_to_show.index.tolist()
    reliable_intervals_for_right_side = intervals_per_side[two_keys_list[1]]
    reliable_intervals_for_left_side = intervals_per_side[two_keys_list[0]]
    for frame in frames_out_of_wanted_ranges:
        found_in_right = False
        found_in_left = False
        for interval in reliable_intervals_for_right_side:
            if frame in np.arange(interval['start'], interval['end'] + 1):
                found_in_right = True
                break
        for interval in reliable_intervals_for_left_side:
            if frame in np.arange(interval['start'], interval['end'] + 1):
                found_in_left = True
                break

        if not found_in_right:
            df_to_show.loc[[frame], right_side_columns] = np.nan
        if not found_in_left:
            df_to_show.loc[[frame], left_side_columns] = np.nan


if __name__ == '__main__':
    op_row_path = '<Enter some path to all_keypoints.csv file>'
    expected_path = os.getcwd() + '<Enter some path to ground truth file (Server/expected_data/csvs/csv file>'
    interp_path = filter_and_interpolate(op_row_path,
                                         output_path='<can be deleted or put some path to generate output to.>')
    import visualizer
    visualizer.plot_multi_graphs_from_other_csvs([interp_path, op_row_path],
                                                 '<can be deleted or put some path to generate output to.>')
