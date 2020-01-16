# Edited by Roee Groiser
from main import *
import cv2
import math
import utils
import extract_frames as f

body_parts = ['NeckX', 'NeckY', 'NeckScore', 'ChestX', 'ChestY', 'ChestScore', 'RShoulderX', 'RShoulderY',
              'RShoulderScore', 'RElbowX', 'RElbowY', 'RElbowScore', 'RWristX', 'RWristY', 'RWristScore', 'LShoulderX',
              'LShoulderY', 'LShoulderScore',
              'LElbowX', 'LElbowY', 'LElbowScore', 'LWristX', 'LWristY', 'LWristScore']


# Recieves args from main (including video path) and params to configure the library
# Creates 3 csv files(all keypoints, valid and invalid ones) and emplace wire-frame.
def get_keypoints_csv_from_video(args, params):

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
                valid_keypoints_df.to_csv("../output/analytical_data/valid_keypoints.csv")
            else:
                invalid_keypoints_df = pd.concat([invalid_keypoints_df, current_frame_df], sort=False)
                # Update csv file
                invalid_keypoints_df.to_csv("../output/analytical_data/invalid_keypoints.csv")

            # Anyway append it to all keypoints
            all_keypoints_df = pd.concat([all_keypoints_df, current_frame_df], sort=False)
            # Update csv file
            all_keypoints_df.to_csv("../output/analytical_data/all_keypoints.csv")

            # and anyway add it to detected
            current_detected_frame_array = [frame_counter, 0 if not is_valid else 1]
            current_detected_frame_df = pd.DataFrame(current_detected_frame_array).T
            current_detected_frame_df.columns = ['Frame Number', 'Detected']
            frame_detected_df = pd.concat([frame_detected_df, current_detected_frame_df], sort=False)
            frame_detected_df.to_csv("../output/analytical_data/is_frame_detected.csv")
        else:
            nan_record = [frame_counter]
            nan_record = nan_record + [math.nan] * len(body_parts)
            nan_record_df = pd.DataFrame(nan_record).T
            nan_record_df.columns = ['Frame Number'] +  body_parts
            all_keypoints_df = pd.concat([all_keypoints_df, nan_record_df], sort=False)
            # Update csv file
            all_keypoints_df.to_csv("../output/analytical_data/all_keypoints.csv")

            current_detected_frame_array = [frame_counter, 0]
            current_detected_frame_df = pd.DataFrame(current_detected_frame_array).T
            current_detected_frame_df.columns = ['Frame Number', 'Detected']
            frame_detected_df = pd.concat([frame_detected_df, current_detected_frame_df], sort=False)
            frame_detected_df.to_csv("../output/analytical_data/is_frame_detected.csv")

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
