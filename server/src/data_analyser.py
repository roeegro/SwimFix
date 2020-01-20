# Edited by Roee Groiser
from main import *
import math
from scipy import spatial
import numpy as np
from numpy import dot
from numpy.linalg import norm
from scipy.optimize import curve_fit
import operator as op
from functools import reduce
from scipy import interpolate
from scipy.signal import argrelextrema, argrelmin

num_dimentions = 2

# TODO: Check how can I use this list from the original file defined in - video_processor.py
body_parts = ['NeckX', 'NeckY', 'NeckScore', 'ChestX', 'ChestY', 'ChestScore', 'RShoulderX', 'RShoulderY',
              'RShoulderScore', 'RElbowX', 'RElbowY', 'RElbowScore', 'RWristX', 'RWristY', 'RWristScore', 'LShoulderX',
              'LShoulderY', 'LShoulderScore',
              'LElbowX', 'LElbowY', 'LElbowScore', 'LWristX', 'LWristY', 'LWristScore']


def make_body_parts_df(valid_keypoints_df, output_dirs):
    cols = ['Frame Number', 'RShoulder_X', 'RShoulder_Y', 'LShoulder_X', 'LShoulder_Y', 'RArm_X',
            'RArm_Y', 'LArm_X', 'LArm_Y', 'RForarm_X', 'RForarm_Y', 'LForarm_X',
            'LForarm_Y']
    vectors_by_frames_df = pd.DataFrame(columns=cols)
    for index, row in valid_keypoints_df.iterrows():
        chest_point = [row['ChestX'], row['ChestY']]
        Lwrist_point = [row['LWristX'], row['LWristY']]
        Lshoulder_point = [row['LShoulderX'], row['LShoulderY']]
        LElbow_point = [row['LElbowX'], row['LElbowY']]
        Rshoulder_point = [row['RShoulderX'], row['RShoulderY']]
        RElbow_point = [row['RElbowX'], row['RElbowY']]
        Rwrist_point = [row['RWristX'], row['RWristY']]

        # Calculations
        row_array = [row['Frame Number']]
        for i in range(num_dimentions):
            row_array.append(chest_point[i] - Rshoulder_point[i])
        for i in range(num_dimentions):
            row_array.append(chest_point[i] - Lshoulder_point[i])
        for i in range(num_dimentions):
            row_array.append(Rshoulder_point[i] - RElbow_point[i])
        for i in range(num_dimentions):
            row_array.append(Lshoulder_point[i] - LElbow_point[i])
        for i in range(num_dimentions):
            row_array.append(RElbow_point[i] - Rwrist_point[i])
        for i in range(num_dimentions):
            row_array.append(LElbow_point[i] - Lwrist_point[i])

        vectors_in_current_frame = pd.DataFrame(row_array).T
        vectors_in_current_frame.columns = cols
        vectors_by_frames_df = pd.concat([vectors_by_frames_df, vectors_in_current_frame], sort=False)
        vectors_by_frames_df.to_csv(output_dirs['analytical_data_path'] + "/vectors_by_time.csv")


def make_angle_df(vectors_df, output_dirs):
    df_angles = pd.DataFrame(columns=['Frame Number', 'RElbow', 'RShoulder', 'LElbow', 'LShoulder'])
    for index, row in vectors_df.iterrows():
        # Calculating vectors (from each 2 points) and
        r_forarm_vector = [(float)(row['RForarm_X']), (float)(row['RForarm_Y'])]
        r_arm_vector = [(float)(row['RArm_X']), (float)(row['RArm_Y'])]

        r_r1_vector = [(float)(row['RShoulder_X']), float(row['RShoulder_Y'])]

        l_forarm_vector = [(float)(row['LForarm_X']), (float)(row['LForarm_Y'])]

        l_arm_vector = [row['LArm_X'], row['LArm_Y']]

        l_r1_vector = [row['LShoulder_X'], row['LShoulder_Y']]

        # Calculating relevant angles
        norm_of_albow_angle = norm(r_arm_vector) * norm(r_forarm_vector)
        if norm_of_albow_angle is math.nan:
            continue
        else:
            neg_r_arm_vector = (list)(map(lambda coor: -coor, r_arm_vector))
            r_elbow_angle = math.degrees(
                np.arccos(dot(neg_r_arm_vector, r_forarm_vector) / norm_of_albow_angle))

        norm_of_r_shoulder__angle = norm(r_r1_vector) * norm(r_arm_vector)
        if norm_of_r_shoulder__angle is math.nan:
            continue
        else:
            neg_r_r1_vector = (list)(map(lambda coor: -coor, r_r1_vector))
            r_shoulder_elbow_angle = math.degrees(
                np.arccos(dot(neg_r_r1_vector, r_arm_vector) / norm_of_r_shoulder__angle))

        norm_of_l_shoulder__angle = norm(l_arm_vector) * norm(l_forarm_vector)
        if norm_of_l_shoulder__angle is math.nan:
            continue
        else:
            neg_l_arm_vector = (list)(map(lambda coor: -coor, l_arm_vector))
            l_elbow_angle = math.degrees(
                np.arccos(dot(neg_l_arm_vector, l_forarm_vector) / norm_of_l_shoulder__angle))

        norm_of_l_elbow__angle = norm(l_r1_vector) * norm(l_arm_vector)
        if norm_of_l_elbow__angle is math.nan:
            continue
        else:
            neg_l_r1_vector = (list)(map(lambda coor: -coor, l_r1_vector))
            l_shoulder_elbow_angle = math.degrees(
                np.arccos(dot(neg_l_r1_vector, l_arm_vector) / norm_of_l_elbow__angle))

        array_of_angles = [row['Frame Number'], r_elbow_angle, r_shoulder_elbow_angle, l_elbow_angle,
                           l_shoulder_elbow_angle]
        current_frame_angles_df = pd.DataFrame(array_of_angles).T
        current_frame_angles_df.columns = df_angles.columns
        df_angles = pd.concat([df_angles, current_frame_angles_df], sort=False)
        df_angles.to_csv(output_dirs['analytical_data_path'] + "/angles_by_time.csv")


def make_body_part_detected_by_frame_df(output_dirs):
    df = pd.read_csv(output_dirs['analytical_data_path'] + '/all_keypoints.csv')
    body_parts_without_coor = []
    for i in range(0, len(body_parts), 3):
        body_part = body_parts[i]
        body_parts_without_coor.extend([body_part[:len(body_part)]])

    cols_of_df = ['Frame Number'] + body_parts_without_coor
    df_to_load = pd.DataFrame(columns=cols_of_df)
    frame_nums = df['Frame Number']
    for col in df.columns:
        if "Score" in col or col == 'Frame Number':
            df = df.drop([col], axis='columns')
    for index, row in df.iterrows():
        body_parts_detected_in_cur_frame_array = []
        for i in range(1, len(df.columns), 2):  # check every pair of 2 cols (x,y for each part)
            if math.isnan(row[i]) and math.isnan(row[i + 1]):  # not detected
                body_parts_detected_in_cur_frame_array.extend([0])
            else:
                body_parts_detected_in_cur_frame_array.extend([1])
        cur_frame_array = [frame_nums[index]] + body_parts_detected_in_cur_frame_array
        cur_frame_df = pd.DataFrame(cur_frame_array).T
        cur_frame_df.columns = df_to_load.columns
        df_to_load = pd.concat([df_to_load, cur_frame_df], sort=False)
        df_to_load.to_csv(output_dirs['analytical_data_path'] + "/body_part_detected_by_frame_df.csv")


def curve(x, a, b, c, d):
    return a * (x ** 3) + b * (x ** 2) + c * x + d


def keypoint_estimation(keypoint_df):
    frame_numbers = keypoint_df['Frame Number']
    keypoint_df.drop(columns=['Frame Number'], axis=1, inplace=True)
    interpolated_keypoint_df = keypoint_df.interpolate()

    # Initial parameter guess, just to kick off the optimization
    guess = (0.5, 0.5, 0.5, 0.5)
    # Create copy of data to remove NaNs for curve fitting
    fit_df = interpolated_keypoint_df.dropna()

    # Place to store function parameters for each column
    col_params = {}

    # Curve fit each column
    for col in fit_df.columns:
        # Get x & y
        x = fit_df.index.astype(float).values
        y = fit_df[col].values
        # Curve fit column and get curve parameters
        params = curve_fit(curve, x, y, guess)
        # Store optimized parameters
        col_params[col] = params[0]

    # Extrapolate each column
    for col in interpolated_keypoint_df.columns:
        # Get the index values for NaNs in the column
        x = interpolated_keypoint_df[pd.isnull(interpolated_keypoint_df[col])].index.astype(float).values
        # Extrapolate those points with the fitted function
        interpolated_keypoint_df.loc[x, col] = curve(x, *col_params[col])

    frame_numbers = range(len(interpolated_keypoint_df))
    interpolated_keypoint_df.insert(loc=0, column='Frame Number', value=frame_numbers)
    interpolated_keypoint_df.drop(columns=['Unnamed: 0'], axis=1, inplace=True)
    return interpolated_keypoint_df


def make_interpolation(output_dirs):
    keypoints_df = pd.read_csv(output_dirs['analytical_data_path'] + '/all_keypoints.csv')
    frame_numbers = range(len(keypoints_df))
    keypoints_df = keypoints_df.drop(columns=['Frame Number', 'Unnamed: 0'], axis=1, inplace=False)
    indexes = []
    for index, row in keypoints_df.iterrows():
        if is_all_row_nans(row):
            indexes.append(index)
        else:
            break
    start_interpolation_from = max(indexes) + 1

    for col in keypoints_df.columns:
        if "Score" in col:
            continue
        for specific_frame in range(start_interpolation_from, len(keypoints_df)):
            if not math.isnan(keypoints_df.iloc[specific_frame][col]):
                continue
            # must interpolate. Interpolation will be done by Gera's way.
            prevs = take_n_prev_keypoints_of_specific_part(keypoints_df, specific_frame, col, 15)
            # nexts = take_n_next_keypoints_of_specific_part(keypoints_df, specific_frame, col, 5)
            # sum_weighted_points = prevs[0] + nexts[0]
            # sum_of_coefs = prevs[1] + nexts[1]
            if prevs[0] == []:
                continue
            # keypoints_df.set_value(specific_frame, col, sum(sum_weighted_points) / sum_of_coefs)
            keypoints_df.set_value(specific_frame, col, sum(prevs[0]) / prevs[1])
    filter_data_in_the_edges(df=keypoints_df, first_index=start_interpolation_from,
                             num_of_frames=10)  # filter data of the first and last 1 seconds.

    keypoints_df.insert(loc=0, column='Frame Number', value=frame_numbers)
    keypoints_df.to_csv(output_dirs['analytical_data_path'] + '/all_keypoints.csv')


def filter_anomalies(output_dirs):
    keypoints_df = pd.read_csv(output_dirs['analytical_data_path'] + '/all_keypoints.csv')
    frame_numbers = range(len(keypoints_df))
    keypoints_df = keypoints_df.drop(columns=['Frame Number', 'Unnamed: 0'], axis=1, inplace=False)
    indexes = []
    for index, row in keypoints_df.iterrows():
        if is_all_row_nans(row):
            indexes.append(index)
        else:
            break
    start_interpolation_from = max(indexes) + 1
    for col in keypoints_df.columns:
        if "Score" in col:
            continue
        for specific_frame in range(start_interpolation_from, len(keypoints_df)):
            set_nan_when_diff_too_high(df=keypoints_df, row=specific_frame, col=col, max_threshold=12)
    filter_data_in_the_edges(keypoints_df, first_index=start_interpolation_from, num_of_frames=10)
    keypoints_df.insert(loc=0, column='Frame Number', value=frame_numbers)
    keypoints_df.to_csv(output_dirs['analytical_data_path'] + '/all_keypoints.csv')


def filter_data_in_the_edges(df, first_index, num_of_frames):
    # df.apply(lambda x: math.nan if x.name in range(first_index, first_index + num_of_frames) or x.name in range(
    #     len(df) - num_of_frames, len(df)) else x, axis=1)
    for row in range(first_index, first_index + num_of_frames):
        for col in df.columns:
            df.set_value(row, col, math.nan)

    for row in range(len(df) - num_of_frames, len(df)):
        for col in df.columns:
            df.set_value(row, col, math.nan)


def set_nan_when_diff_too_high(df, row, col, max_threshold):
    if row == len(df) - 1:
        return
    cur_val = df.iloc[row][col]
    next_frame_index = find_next_non_nan_row_index(df, row)
    next_val = df.iloc[next_frame_index][col]
    if math.isnan(cur_val) or math.isnan(next_val):
        return
    if math.fabs(next_val - cur_val) / math.fabs(next_frame_index - row) > max_threshold:
        df.set_value(row, col, math.nan)
        df.set_value(row + 1, col, math.nan)


def is_all_row_nans(row):
    for col in row:
        if not math.isnan(col):
            return False
    return True


def find_next_non_nan_row_index(df, index):
    ret = index + 1
    while ret < len(df):
        if not is_all_row_nans(df.iloc[ret]):
            return ret
        ret += 1
    return -1


def take_n_prev_keypoints_of_specific_part(df, cur_index, col, n):
    # if cur_index - i < 0:
    #     return []
    # sub_df = df.iloc[cur_index - i:cur_index]
    # lst = sub_df.loc[:, col].to_list()
    # to_return = list(filter(lambda element: not math.isnan(element), lst))
    # return to_return
    print("We want 5 prev indexes of {}".format(cur_index))
    found_index = cur_index
    to_return = []
    sum_coef = 0
    for i in range(0, n):
        found_index = find_prev_non_nan_row_index_by_col(df, found_index, col)
        print("Found {}".format(found_index))
        if found_index == -1:
            print("You steped too back!")
            break
        value = df.iloc[found_index][col]
        binomial_coef = ncr(2 * n, n - i - 1)
        sum_coef += binomial_coef
        to_return.append(binomial_coef * value)
    return to_return, sum_coef


def take_n_next_keypoints_of_specific_part(df, cur_index, col, n):
    # if cur_index + i >= len(df):
    #     return []
    # sub_df = df.iloc[cur_index + 1: cur_index + i + 1]
    # lst = sub_df.loc[:, col].to_list()
    # to_return = list(filter(lambda element: not math.isnan(element), lst))
    print("We want 5 next indexes of {}".format(cur_index))
    found_index = cur_index
    to_return = []
    sum_coef = 0
    for i in range(0, n):
        found_index = find_next_non_nan_row_index_by_col(df, found_index, col)
        if found_index == -1:
            print("you steped too far")
            break
        print("Found next with index {}".format(found_index))
        value = df.iloc[found_index][col]
        binomial_coef = ncr(2 * n, n - i - 1)
        sum_coef += binomial_coef
        to_return.append(binomial_coef * value)
    return to_return, sum_coef


def find_next_non_nan_row_index_by_col(df, index, col):
    ret = index + 1
    while ret < len(df):
        if not math.isnan(df.iloc[ret][col]):
            return ret
        ret += 1
    return -1


def find_prev_non_nan_row_index_by_col(df, index, col):
    ret = index - 1
    while ret >= 0:
        if not math.isnan(df.iloc[ret][col]):
            return ret
        ret -= 1
    return -1


def ncr(n, r):
    r = min(r, n - r)
    numer = reduce(op.mul, range(n, n - r, -1), 1)
    denom = reduce(op.mul, range(1, r + 1), 1)
    return numer / denom


def nan_helper(y):
    """Helper to handle indices and logical indices of NaNs.

    Input:
        - y, 1d numpy array with possible NaNs
    Output:
        - nans, logical indices of NaNs
        - index, a function, with signature indices= index(logical_indices),
          to convert logical indices of NaNs to 'equivalent' indices
    Example:
        >>> # linear interpolation of NaNs
        >>> nans, x= nan_helper(y)
        >>> y[nans]= np.interp(x(nans), x(~nans), y[~nans])
    """

    return np.isnan(y), lambda z: z.nonzero()[0]


def create_interpolated_csv(csv_path, y_cols, x_col='Frame Number', output_path='output'):
    df = pd.read_csv(csv_path)
    if type(y_cols) == str:
        y_cols = [y_cols]
    cols = y_cols + [x_col]
    df.drop(columns=df.columns.difference(cols), axis=1, inplace=True)
    for col_name in y_cols:
        # Numpy Interpolation
        # y = df[col_name]
        # nans, x = nan_helper(y)
        # y[nans] = np.interp(x(nans), x(~nans), y[~nans])

        # Pandas Interpolation
        first_notna_frame = df[col_name].notna().idxmax()
        last_notna_frame = df[col_name].notna()[::-1].idxmax()
        df = df.iloc[first_notna_frame:last_notna_frame + 1]
        df.reset_index(drop=True, inplace=True)
        df = df[df.columns.dropna()]
        df[col_name].interpolate(method='cubic', inplace=True)

        y = df[col_name].values
        x = df['Frame Number'].values
        xnew = np.linspace(x.min(), x.max(), len(x))
        bspline = interpolate.make_interp_spline(x, y)
        y_smoothed = bspline(xnew)
        df[col_name] = y_smoothed

    path = output_path + '/' + '_'.join(y_cols) + '.csv'
    df.to_csv(path)
    return path


def calc_avg_period(csv_path, col_names, min_period=1.5, frame_rate=30, maximum=True, avg=False):
    df = pd.read_csv(csv_path)
    all_keypoints_csv_path = '../../all_keypoints.csv'
    all_df = pd.read_csv(all_keypoints_csv_path)
    if type(col_names) == str:
        col_names = [col_names]
    avg_per_dict = {}
    for col_name in col_names:
        data = df[col_name]
        if maximum:
            extremum_indices = argrelextrema(data.values, np.greater)[0]
        else:
            extremum_indices = argrelmin(data.values)[0]
        periods = []
        min_period_frames = frame_rate * min_period
        i = 0
        period_num = 1
        while i < len(extremum_indices) - 1:
            j = i + 1
            found = False
            while j < len(extremum_indices) - 1 and not found:
                period_frames = extremum_indices[j] - extremum_indices[i]
                if period_frames >= min_period_frames:
                    periods.append(round(period_frames / frame_rate, 3))
                    found = True
                else:
                    j += 1
            i = j
        avg_per_dict[col_name] = (periods, np.average(periods))
    if len(avg_per_dict) == 1:
        return avg_per_dict[col_names[0]][1]
    elif avg:
        l = list(map(lambda x: x[1], avg_per_dict.values()))
        return round(np.average(l), 3)
    else:
        return avg_per_dict
    # return round(np.average(periods)/frame_rate, 3)

# def get_confidence_score(csv_path, frames):
#     df = pd.read_csv(csv_path)
