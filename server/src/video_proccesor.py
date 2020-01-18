# Edited by Roee Groiser
from main import *
import cv2
import math
import utils

from stat import S_ISREG, ST_CTIME, ST_MODE
import os, sys, time
from functools import reduce
import extract_frames as f
import extract_poses as p
import canada as c
body_parts = ['NeckX', 'NeckY', 'NeckScore', 'ChestX', 'ChestY', 'ChestScore', 'RShoulderX', 'RShoulderY',
              'RShoulderScore', 'RElbowX', 'RElbowY', 'RElbowScore', 'RWristX', 'RWristY', 'RWristScore', 'LShoulderX',
              'LShoulderY', 'LShoulderScore',
              'LElbowX', 'LElbowY', 'LElbowScore', 'LWristX', 'LWristY', 'LWristScore']


# Recieves args from main (including video path) and params to configure the library
# Creates 3 csv files(all keypoints, valid and invalid ones) and emplace wire-frame.
def get_keypoints_csv_from_video(args, params):
    video_name = utils.get_file_name(args[0].image_path)
    video_name = utils.filename_without_prefix(video_name)
    output_dirs = utils.generate_dirs_for_output_of_movie(video_name)

    # Extract frames
    f.extract_frames_by_file(file=args[0].image_path, output=output_dirs['output_movie_dir'])

    # # sort frames by creation time
    # # path to the directory (relative or absolute)
    # dirpath = output_dirs['output_movie_dir'] + '\\frames'
    # list_of_frames = [name for name in os.listdir(dirpath)]
    # frame_to_index = list(map(lambda  file_name : {'path':file_name ,'index':utils.get_id_of_file(utils.filename_without_prefix(file_name))} , list_of_frames))
    # frame_to_index = sorted(frame_to_index, key=lambda k: (int)(k['index']))
    # params['image_dir'] = output_dirs['output_movie_dir'] + '\\frames'
    # params['write_images'] =output_dirs['output_movie_dir'] + '\\images'
    # # Starting OpenPose
    # opWrapper = op.WrapperPython()
    # # print(params)
    # opWrapper.configure(params)
    # opWrapper.start()
    # datum = op.Datum()
    #
    # for i in range(0,len(frame_to_index)-1):
    #     print(i)
    #     frame = cv2.imread(dirpath + '\\'+ frame_to_index[i]['path'])
    #     datum.cvInputData = frame
    #     opWrapper.emplaceAndPop([datum])
    #     output = datum.poseKeypoints
    #     cv2.waitKey(10)
    #     cv2.imshow("OpenPose 1.5.1 - Tutorial Python API", datum.cvOutputData)
    #     converter = op.OpOutputToCvMat()
    #     cv2.imwrite(output_dirs['output_movie_dir'] + '\\images',converter.formatToCvMat(datum.cvOutputData))
    # cv2.destroyAllWindows()

    # Starting OpenPose
    opWrapper = op.WrapperPython()
    # print(params)
    opWrapper.configure(params)
    opWrapper.start()

    # Process Image
    datum = op.Datum()
    print("path is {}".format(args[0].image_path))
    cap = cv2.VideoCapture(args[0].image_path)
    valid_keypoints_df = pd.DataFrame(columns=['Frame Number'] + body_parts)
    invalid_keypoints_df = pd.DataFrame(columns=['Frame Number'] + body_parts)
    all_keypoints_df = pd.DataFrame(columns=['Frame Number'] + body_parts)
    frame_detected_df = pd.DataFrame(columns=['Frame Number', 'Detected'])
    frame_counter = 0
    while cap.isOpened():
        check, frame = cap.read()
        if not check:
            break
        resized_frame = cv2.resize(frame, (600, 480), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
        # resized_frame = cv2.resize(frame, dsize=(720, 480))
        datum.cvInputData = resized_frame
        opWrapper.emplaceAndPop([datum])
        output = datum.poseKeypoints

        # Extracting points coordinates into csv file
        if not datum.poseKeypoints.shape == ():
            first_person = output[0]
            current_frame_array = []

            # make representation of each relevant point
            for i, body_part in enumerate(first_person):
                if i < len(body_parts) / 3:  # take only 8 first points which are relevant to our detection
                    xCoor = body_part[0]
                    yCoor = body_part[1]
                    score = body_part[2]
                    if xCoor == 0:
                        xCoor = math.nan
                    if yCoor == 0:
                        yCoor = math.nan
                    if score == 0:
                        score = math.nan
                    current_frame_array += [xCoor, yCoor, score]

            # Concatenate record of current frame number
            current_frame_array = [frame_counter] + current_frame_array
            current_frame_df = pd.DataFrame(
                current_frame_array).T  # make the array as a line to be concatenated to in the csv.
            # Concatenate from left new feature of Number frame
            current_frame_df.columns = ['Frame Number'] + body_parts
            # if has no basic anomaly - append it to valid keypoints df. Otherwise - to invalid keypoints
            is_valid = valid_frame(current_frame_df.loc[:, 'NeckX':])
            if is_valid:  # Check the dataframe without the number frame property
                valid_keypoints_df = pd.concat([valid_keypoints_df, current_frame_df], sort=False)
                # Update csv file
                valid_keypoints_df.to_csv(output_dirs['analytical_data_path'] + "/valid_keypoints.csv")
            else:
                invalid_keypoints_df = pd.concat([invalid_keypoints_df, current_frame_df], sort=False)
                # Update csv file
                invalid_keypoints_df.to_csv(output_dirs['analytical_data_path'] + "/invalid_keypoints.csv")

            # Anyway append it to all keypoints
            all_keypoints_df = pd.concat([all_keypoints_df, current_frame_df], sort=False)
            # Update csv file
            all_keypoints_df.to_csv(output_dirs['analytical_data_path'] + "/all_keypoints.csv")

            # and anyway add it to detected
            current_detected_frame_array = [frame_counter, 0 if not is_valid else 1]
            current_detected_frame_df = pd.DataFrame(current_detected_frame_array).T
            current_detected_frame_df.columns = ['Frame Number', 'Detected']
            frame_detected_df = pd.concat([frame_detected_df, current_detected_frame_df], sort=False)
            frame_detected_df.to_csv(output_dirs['analytical_data_path'] + "/is_frame_detected.csv")
        else:
            nan_record = [frame_counter]
            nan_record = nan_record + [math.nan] * len(body_parts)
            nan_record_df = pd.DataFrame(nan_record).T
            nan_record_df.columns = ['Frame Number'] + body_parts
            all_keypoints_df = pd.concat([all_keypoints_df, nan_record_df], sort=False)
            # Update csv file
            all_keypoints_df.to_csv(output_dirs['analytical_data_path'] + "/all_keypoints.csv")

            current_detected_frame_array = [frame_counter, 0]
            current_detected_frame_df = pd.DataFrame(current_detected_frame_array).T
            current_detected_frame_df.columns = ['Frame Number', 'Detected']
            frame_detected_df = pd.concat([frame_detected_df, current_detected_frame_df], sort=False)
            frame_detected_df.to_csv(output_dirs['analytical_data_path'] + "/is_frame_detected.csv")

        # if not args[0].no_display:
        cv2.imshow("body from video", datum.cvOutputData)
        # outputVideo.write(datum.cvOutputData)
        # out.write(datum.cvOutputData)
        key = cv2.waitKey(1)
        # if key == 27: break
        frame_counter += 1

    # When everything done, release
    # the video capture object
    print("finished")
    cap.release()
    # Closes all the frames
    cv2.destroyAllWindows()

    # Display Image
    # print("Body keypoints: \n" + str(datum.poseKeypoints))
    # cv2.imshow("OpenPose 1.5.1 - Tutorial Python API", datum.cvOutputData)
    # cv2.waitKey(0)
    return output_dirs


# Basic check if frame is valid to be included in the analytical data
# Checks if critic data (Elbows,Shoulders...) is 0
def valid_frame(current_frame_df):
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
