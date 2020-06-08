import pandas as pd
import numpy as np
import cv2
import output_manager
import os

errors_df = None


def check_left_hand_crossed_the_middle_line(all_kp_df, angles_df,name):
    error_id = get_id_of_error(name)
    for index, __ in all_kp_df.iterrows():
        l_wrist_x = all_kp_df['LWristX'][index]
        l_wrist_y = all_kp_df['LWristY'][index]
        l_elbow_x = all_kp_df['LWristX'][index]
        l_elbow_y = all_kp_df['LElbowX'][index]
        neck_x = all_kp_df['NeckX'][index]
        neck_y = all_kp_df['NeckY'][index]
        if l_elbow_x < neck_x:
            print('error 3')
            from_point = (int(neck_x), int(neck_y))
            to_point = (int(neck_x), int(l_elbow_y))
            draw_line(index, from_point, to_point)
            if error_id != -1 and index not in errors_df['frames'][error_id]:
                print('detected error in frame number {}'.format(index))
                errors_df['frames'][error_id] = errors_df['frames'][error_id] + [index]
        if l_wrist_x < neck_x:
            print('error 4')
            from_point = (int(neck_x), int(neck_y))
            to_point = (int(neck_x), int(l_wrist_y))
            draw_line(index, from_point, to_point)
            if error_id != -1 and index not in errors_df['frames'][error_id]:
                print('detected error in frame number {}'.format(index))
                errors_df['frames'][error_id] = errors_df['frames'][error_id] + [index]


def check_right_hand_crossed_the_middle_line(all_kp_df, angles_df,name):
    error_id = get_id_of_error(name)
    for index, __ in all_kp_df.iterrows():
        r_wrist_x = all_kp_df['RWristX'][index]
        r_wrist_y = all_kp_df['RWristY'][index]
        r_elbow_x = all_kp_df['RElbowX'][index]
        r_elbow_y = all_kp_df['RElbowY'][index]
        neck_x = all_kp_df['NeckX'][index]
        neck_y = all_kp_df['NeckY'][index]
        if r_elbow_x > neck_x:
            print('error 1')
            from_point = (int(neck_x), int(neck_y))
            to_point = (int(neck_x), int(r_elbow_y))
            draw_line(index, from_point, to_point)
            if error_id != -1 and index not in errors_df['frames'][error_id]:
                print('detected error in frame number {}'.format(index))
                errors_df['frames'][error_id] = errors_df['frames'][error_id] + [index]
        if r_wrist_x > neck_x:
            print('error 2')
            from_point = (int(neck_x), int(neck_y))
            to_point = (int(neck_x), int(r_wrist_y))
            draw_line(index, from_point, to_point)
            if error_id != -1 and index not in errors_df['frames'][error_id]:
                print('detected error in frame number {}'.format(index))
                errors_df['frames'][error_id] = errors_df['frames'][error_id] + [index]



def draw_line(frame_index, from_point, to_point):
    frame_index = int(frame_index)
    frame_path = output_manager.get_output_dirs_dict()['swimfix_frames_path'] + '/swimfix_annotated_frame_{}.jpg'.format(frame_index)
    frame = cv2.imread(frame_path)
    annotated_frame = cv2.line(frame, to_point, from_point, (255, 0, 0))
    cv2.imwrite(frame_path, annotated_frame)


errors = [{'check_left_hand_crossed_the_middle_line': check_left_hand_crossed_the_middle_line},{'check_right_hand_crossed_the_middle_line',check_right_hand_crossed_the_middle_line}]


def perfomance_evaluator(all_kp_path, angles_path, output_path=None):
    all_kp_df = pd.read_csv(all_kp_path).set_index('Frame Number')
    angles_df = pd.read_csv(angles_path).set_index('Frame Number')
    global errors_df
    errors_df = pd.DataFrame({'error_id': np.arange(0, len(errors)), 'frames': [[] * len(errors)]}).set_index('error_id')
    error_map_df = pd.DataFrame({'error_id': np.arange(0, len(errors)),
                                 'description': [list(error.keys())[0].replace('check_', '').replace('_', ' ') for error
                                                 in errors]}).set_index('error_id')

    output_directory = output_manager.get_output_dir_path(key="time_path") if output_path is None else output_path
    error_map_df.to_csv(output_directory + '/map.csv',index=False)
    for potential_error in errors:
        (list(potential_error.values())[0])(all_kp_df, angles_df,list(potential_error.keys())[0])

    errors_df.to_csv(output_directory + '/swimmer_errors.csv',index=False)
    errors_df = None


def get_id_of_error(error_name):
    for i, error in enumerate(errors):
        if list(error.keys())[0] == error_name:
            return i
    return -1


if __name__ == '__main__':
    perfomance_evaluator(os.getcwd() + '/interpolated_and_filtered_all_keypoints.csv', os.getcwd() + '/angles.csv',
                         output_path=os.getcwd())
