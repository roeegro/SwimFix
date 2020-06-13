import evaluator
import math
def check_if_global_forearm_angle_not_in_valid_range(all_kp_df, angles_df, name, side,error_names,errors_df, inner_angle=45,
                                                     outer_angle=10):
    
    if side not in ['L', 'R']:
        return
    error_id = evaluator.get_id_of_error(name,error_names_for_external_calling = error_names)
    for index, __ in all_kp_df.iterrows():
        global_forearm_angle = angles_df[side + 'GlobalForeArmAng'][index]
        wrist_x = all_kp_df[side + 'WristX'][index]
        wrist_y = all_kp_df[side + 'WristY'][index]
        elbow_x = all_kp_df[side + 'ElbowX'][index]
        if (wrist_x > elbow_x and global_forearm_angle > inner_angle) or (
                wrist_x < elbow_x and global_forearm_angle > outer_angle):
            elbow_y = all_kp_df[side + 'ElbowY'][index]
            elbow_pos = (int(elbow_x), int(elbow_y))
            forearm_length = math.sqrt(
                math.pow(all_kp_df[side + 'ElbowX'][index] - all_kp_df[side + 'WristX'][index], 2) + math.pow(
                    all_kp_df[side + 'ElbowY'][index] - all_kp_df[side + 'WristY'][index], 2))
            wrist_x_recommended_for_inner_angle = elbow_x + (
                    math.sin(math.radians(inner_angle)) * forearm_length)
            wrist_y_recommended_for_inner_angle = elbow_y + (
                    math.cos(math.radians(inner_angle)) * forearm_length)
            wrist_x_recommended_for_outer_angle = wrist_x - (
                    -math.sin(math.radians(outer_angle)) * forearm_length)
            wrist_y_recommended_for_outer_angle = wrist_y + (
                    math.cos(math.radians(outer_angle)) * forearm_length)
            wrist_pos_for_min_recommended_angle = (
                int(wrist_x_recommended_for_inner_angle), int(wrist_y_recommended_for_inner_angle))
            wrist_pos_for_max_recommended_angle = (
                int(wrist_x_recommended_for_outer_angle), int(wrist_y_recommended_for_outer_angle))
            evaluator.draw_line(index, elbow_pos, wrist_pos_for_min_recommended_angle)
            evaluator.draw_line(index, elbow_pos, wrist_pos_for_max_recommended_angle)
            if error_id != -1 and index not in errors_df['frames'][error_id]:
                errors_df['frames'][error_id] = errors_df['frames'][error_id] + [index]
                
               
check_if_global_forearm_angle_not_in_valid_range(all_kp_df, angles_df, name, side,error_names,errors_df)