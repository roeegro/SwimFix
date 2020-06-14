import pandas as pd
import numpy as np
import cv2
import output_manager
import os
import math
import utils
import types

errors_df = None


def check_if_hand_crossed_the_middle_line(index, all_kp_df, angles_df, name, side):
    if side not in ['L', 'R']:
        return
    error_weight = 0
    error_id = get_id_of_error(name)
    wrist_x = all_kp_df[side + 'WristX'][index]
    wrist_y = all_kp_df[side + 'WristY'][index]
    elbow_x = all_kp_df[side + 'WristX'][index]
    neck_x = all_kp_df['NeckX'][index]
    neck_y = all_kp_df['NeckY'][index]
    palm_x_loc = calculate_palm_x_loc(wrist_x, elbow_x)
    if palm_x_loc < neck_x:
        from_point = (int(neck_x), int(neck_y))
        to_point = (int(neck_x), int(wrist_y))
        draw_line(index, from_point, to_point, selected_bgr_color=(0, 128, 255))
        if error_id != -1 and index not in errors_df['frames'][error_id]:
            errors_df['frames'][error_id] = errors_df['frames'][error_id] + [index]
            error_weight += 1.5
            errors_df['points_reduced'][error_id] = errors_df['points_reduced'][error_id] + error_weight


def check_if_elbow_angle_not_in_valid_range(index, all_kp_df, angles_df, name, side):
    if side not in ['L', 'R']:
        return
    error_weight = 0
    min_angle_recommended = 90
    max_angle_recommended = 175
    error_id = get_id_of_error(name)
    elbow_angle = angles_df[side + 'ElbowAng'][index]
    if elbow_angle > max_angle_recommended or elbow_angle < min_angle_recommended:
        elbow_x = all_kp_df[side + 'ElbowX'][index]
        elbow_y = all_kp_df[side + 'ElbowY'][index]
        elbow_pos = (int(elbow_x), int(elbow_y))
        forearm_length = math.sqrt(
            math.pow(all_kp_df[side + 'ElbowX'][index] - all_kp_df[side + 'WristX'][index], 2) + math.pow(
                all_kp_df[side + 'ElbowY'][index] - all_kp_df[side + 'WristY'][index], 2))
        wrist_x_recommended_for_min_angle = elbow_x + (
                math.cos(math.radians(min_angle_recommended)) * forearm_length)
        wrist_y_recommended_for_min_angle = elbow_y + (
                math.sin(math.radians(min_angle_recommended)) * forearm_length)
        wrist_x_recommended_for_max_angle = elbow_x + (
                math.cos(math.radians(max_angle_recommended)) * forearm_length)
        wrist_y_recommended_for_max_angle = elbow_y + (
                math.sin(math.radians(max_angle_recommended)) * forearm_length)
        wrist_pos_for_min_recommended_angle = (
            int(wrist_x_recommended_for_min_angle), int(wrist_y_recommended_for_min_angle))
        wrist_pos_for_max_recommended_angle = (
            int(wrist_x_recommended_for_max_angle), int(wrist_y_recommended_for_max_angle))
        draw_line(index, elbow_pos, wrist_pos_for_min_recommended_angle, selected_bgr_color=(128, 0, 128))
        draw_line(index, elbow_pos, wrist_pos_for_max_recommended_angle)
        if error_id != -1 and index not in errors_df['frames'][error_id]:
            errors_df['frames'][error_id] = errors_df['frames'][error_id] + [index]
            error_weight += 1.5
            errors_df['points_reduced'][error_id] = errors_df['points_reduced'][error_id] + error_weight


# def check_if_global_forearm_angle_not_in_valid_range(all_kp_df, angles_df, name, side, inner_angle=45,
#                                                      outer_angle=10):
#     if side not in ['L', 'R']:
#         return
#     error_id = get_id_of_error(name)
#     for index, __ in all_kp_df.iterrows():
#         global_forearm_angle = angles_df[side + 'GlobalForeArmAng'][index]
#         wrist_x = all_kp_df[side + 'WristX'][index]
#         wrist_y = all_kp_df[side + 'WristY'][index]
#         elbow_x = all_kp_df[side + 'ElbowX'][index]
#         if (wrist_x > elbow_x and global_forearm_angle > inner_angle) or (
#                 wrist_x < elbow_x and global_forearm_angle > outer_angle):
#             elbow_y = all_kp_df[side + 'ElbowY'][index]
#             elbow_pos = (int(elbow_x), int(elbow_y))
#             forearm_length = math.sqrt(
#                 math.pow(all_kp_df[side + 'ElbowX'][index] - all_kp_df[side + 'WristX'][index], 2) + math.pow(
#                     all_kp_df[side + 'ElbowY'][index] - all_kp_df[side + 'WristY'][index], 2))
#             wrist_x_recommended_for_inner_angle = elbow_x + (
#                     math.sin(math.radians(inner_angle)) * forearm_length)
#             wrist_y_recommended_for_inner_angle = elbow_y + (
#                     math.cos(math.radians(inner_angle)) * forearm_length)
#             wrist_x_recommended_for_outer_angle = wrist_x - (
#                     -math.sin(math.radians(outer_angle)) * forearm_length)
#             wrist_y_recommended_for_outer_angle = wrist_y + (
#                     math.cos(math.radians(outer_angle)) * forearm_length)
#             wrist_pos_for_min_recommended_angle = (
#                 int(wrist_x_recommended_for_inner_angle), int(wrist_y_recommended_for_inner_angle))
#             wrist_pos_for_max_recommended_angle = (
#                 int(wrist_x_recommended_for_outer_angle), int(wrist_y_recommended_for_outer_angle))
#             draw_line(index, elbow_pos, wrist_pos_for_min_recommended_angle)
#             draw_line(index, elbow_pos, wrist_pos_for_max_recommended_angle)
#             if error_id != -1 and index not in errors_df['frames'][error_id]:
#                 errors_df['frames'][error_id] = errors_df['frames'][error_id] + [index]


def draw_line(frame_index, from_point, to_point, selected_bgr_color=(255, 0, 0)):
    frame_index = int(frame_index)
    frame_path = output_manager.get_output_dirs_dict()[
                     'swimfix_frames_path'] + '/swimfix_annotated_frame_{}.jpg'.format(frame_index)
    # frame_path = os.getcwd() + '/../output/roeegro/MVI_8012_from_frame_30/2020-06-12/14-22-41/swimfix_annotated_frames/swimfix_annotated_frame_{}.jpg'.format(
    #     frame_index)
    frame = cv2.imread(frame_path)
    annotated_frame = cv2.line(frame, to_point, from_point, selected_bgr_color)
    cv2.imwrite(frame_path, annotated_frame)


# error_detectors = [check_if_hand_crossed_the_middle_line, check_if_elbow_angle_not_in_valid_range,
#                    check_if_global_forearm_angle_not_in_valid_range]
init_error_detectors = [check_if_hand_crossed_the_middle_line, check_if_elbow_angle_not_in_valid_range]
init_error_names = []
error_detectors = [check_if_hand_crossed_the_middle_line, check_if_elbow_angle_not_in_valid_range]
error_names = []


def perfomance_evaluator(all_kp_path, angles_path, output_path=None):
    all_kp_df = pd.read_csv(all_kp_path).set_index('Frame Number')
    angles_df = pd.read_csv(angles_path).set_index('Frame Number')
    global errors_df
    global error_detectors
    global error_names

    output_directory = output_manager.get_output_dir_path(key="time_path") if output_path is None else output_path

    sides = {'L': 'left', 'R': 'right'}
    error_id = 0
    plug_and_play_dir_path = utils.get_plug_and_play_functions_dir()

    for file_name in os.listdir(plug_and_play_dir_path):
        if os.path.splitext(file_name)[-1] == '.py':
            error_detectors.append(str(file_name))
            # exec(open(plug_and_play_dir_path + '/' + file_name).read(), {'all_kp_df':all_kp_df, 'angles_df':angles_df, 'name': 'check_if_working', 'side':'L'})

    errors_df = pd.DataFrame(
        {'error_id': np.arange(0, len(error_detectors) * 2), 'frames': [[]] * (2 * len(error_detectors)),
         'points_reduced': [0] * (2 * len(error_detectors))}).set_index(
        'error_id')
    errors_df['points_reduced'] = errors_df['points_reduced'].astype('float')
    error_map_df = pd.DataFrame(columns=['error_id', 'description'])
    # definition of errors
    for potential_error in error_detectors:
        for side_entry in sides.items():
            if isinstance(potential_error, types.FunctionType):
                print('is function')
                description = potential_error.__name__.replace('check_', '').replace('_', ' ').replace('if',
                                                                                                       side_entry[1])
            elif isinstance(potential_error, str):
                print('is str')
                description = potential_error.replace('check_', '').replace('_', ' ').replace('if',
                                                                                              side_entry[1]).replace(
                    '.py', '')
            error_names.append(description)
            new_error_to_add = {'error_id': error_id,
                                'description': description}
            error_id += 1
            error_map_df = error_map_df.append(new_error_to_add, ignore_index=True)

    for index, frame in angles_df.iterrows():
        # go over potential errors for both sides.
        for potential_error in error_detectors:
            for side_entry in sides.items():
                if isinstance(potential_error, types.FunctionType):
                    description = potential_error.__name__.replace('check_', '').replace('_', ' ').replace('if',
                                                                                                           side_entry[
                                                                                                               1])
                    potential_error(index, all_kp_df, angles_df, description, side_entry[0])
                elif isinstance(potential_error, str):
                    description = potential_error.replace('check_', '').replace('_', ' ').replace('if',
                                                                                                  side_entry[
                                                                                                      1]).replace('.py',
                                                                                                                  '')

                    exec(open(plug_and_play_dir_path + '/' + potential_error).read(),
                         {"index": index, "all_kp_df": all_kp_df, "angles_df": angles_df, "name": description,
                          "side": side_entry[0],
                          "error_names": error_names, "errors_df": errors_df})

    errors_df = error_map_df.join(errors_df)
    # errors_df = errors_df[len(errors_df['frames']) == []]
    final_grade = evaluate_final_grade()


    errors_df = errors_df.append({'frames': math.nan, 'points_reduced': final_grade}, ignore_index=True)
    errors_df = errors_df[errors_df['frames'].str.len() > 0]

    new_error_to_add = {'frames': np.nan,
                        'description': 'final grade',
                        'points_reduced' : final_grade}
    errors_df = errors_df.append(new_error_to_add, ignore_index=True)
    errors_df.to_csv(output_directory + '/swimmer_errors.csv', index=False)
    # error_map_df.to_csv(output_directory + '/map.csv', index=False)
    errors_df = None
    error_detectors = init_error_detectors
    error_names = init_error_names


def evaluate_final_grade():
    final_grade = 100
    for index, record in errors_df.iterrows():
        final_grade -= errors_df['points_reduced'][index]
    return final_grade


def get_id_of_error(error_name, error_names_for_external_calling=None):
    if error_names_for_external_calling is None:
        global error_names
    else:
        error_names = error_names_for_external_calling

    for i, error in enumerate(error_names):
        if error == error_name:
            return i
    return -1


def calculate_palm_x_loc(wrist_x_loc, elbow_x_loc):
    return ((wrist_x_loc - elbow_x_loc) * 0.37) + elbow_x_loc


def get_defined_error_list():
    plug_and_play_dir_path = utils.get_plug_and_play_functions_dir()
    errors_descriptions = list()
    for error_detector in error_detectors:
        description_to_add = error_detector.__name__.replace('check_', '').replace('_', ' ').replace('if', 'left')
        errors_descriptions.append(description_to_add)
        description_to_add = description_to_add.replace('left', 'right')
        errors_descriptions.append(description_to_add)
    for file_name in os.listdir(plug_and_play_dir_path):
        if os.path.splitext(file_name)[-1] == '.py':
            plug_and_play_func_description = file_name.replace('check_', '').replace('_', ' ').replace('if',
                                                                                                       'left').replace(
                '.py',
                '')
            errors_descriptions.append(plug_and_play_func_description)
            plug_and_play_func_description = plug_and_play_func_description.replace('left', 'right')
            errors_descriptions.append(plug_and_play_func_description)
    print(errors_descriptions)
    return errors_descriptions


if __name__ == '__main__':
    # get_defined_error_list()
    perfomance_evaluator(os.getcwd() + '/interpolated_and_filtered_all_keypoints.csv', os.getcwd() + '/angles.csv',
                         output_path=os.getcwd())
