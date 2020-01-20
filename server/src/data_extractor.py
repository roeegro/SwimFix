# Edited by Roee Groiser and Tom Marzea
from main import *
import math
import numpy as np
from numpy import dot
from numpy.linalg import norm
import operator as op
from functools import reduce

num_dimentions = 2

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


def ncr(n, r):
    r = min(r, n - r)
    numer = reduce(op.mul, range(n, n - r, -1), 1)
    denom = reduce(op.mul, range(1, r + 1), 1)
    return numer / denom