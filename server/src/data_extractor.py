# Edited by Roee Groiser and Tom Marzea
import math

import cv2
import numpy as np
from numpy.linalg import norm
from scipy import interpolate

import extract_frames as f
import utils
import pandas as pd


def generate_vectors_csv(csv_path, filename):
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
                         'RChestX': frame['RShoulderX'] - frame['ChestX'],
                         'RChestY': frame['RShoulderY'] - frame['ChestY'],
                         'LChestX': frame['LShoulderX'] - frame['ChestX'],
                         'LChestY': frame['LShoulderY'] - frame['ChestY'],
                         'RArmX': frame['RShoulderX'] - frame['RElbowX'],
                         'RArmY': frame['RShoulderY'] - frame['RElbowY'],
                         'LArmX': frame['LShoulderX'] - frame['LElbowX'],
                         'LArmY': frame['LShoulderY'] - frame['LElbowY'],
                         'RForearmX': frame['RElbowX'] - frame['RWristX'],
                         'RForearmY': frame['RElbowY'] - frame['RWristY'],
                         'LForearmX': frame['LElbowX'] - frame['LWristX'],
                         'LForearmY': frame['RElbowY'] - frame['RWristY'], }
        vectors_df = vectors_df.append(frame_vectors, ignore_index=True)
    outp_path = utils.get_analytics_dir() + '/' + filename
    pd.DataFrame.to_csv(vectors_df, outp_path, index=False)
    return outp_path


def dotproduct(v1, v2):
    return sum((a * b) for a, b in zip(v1, v2))


def length(v):
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


def generate_angles_csv(csv_path, filname):
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
                        'RShoulderAng': angle(tuple([-1 * x for x in RChestVec]), RArmVec),
                        'LShoulderAng': angle(tuple([-1 * x for x in LChestVec]), LArmVec),
                        'RElbowAng': angle(tuple([-1 * x for x in RArmVec]), RForearmVec),
                        'LElbowAng': angle(tuple([-1 * x for x in LArmVec]), LForearmVec),
                        }
        angles_df = angles_df.append(frame_angels, ignore_index=True)
    outp_path = utils.analytical_df_to_csv(angles_df, filname)
    # pd.DataFrame.to_csv(angles_df, filname, index=False)
    return outp_path


def generate_detected_keypoints_csv(csv_path, score_cols=None, filename=None):
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
    path = utils.get_analytics_dir() + '/' + filename
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


def generate_interpolated_csv(csv_path, y_cols=None, x_col='Frame Number', filename=None):
    df = pd.read_csv(csv_path)
    output_path = utils.get_analytics_dir()
    if y_cols is None:
        cols = list(filter(lambda name: 'Score' not in name, df.columns.values))[1:]
        y_cols = cols.copy()
        y_cols.remove(x_col)
        path = output_path + '/interpolated_' + utils.filename_without_suffix(utils.get_file_name(csv_path)) + '.csv'
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
        # Numpy Interpolation
        # y = df[col_name]
        # nans, x = nan_helper(y)
        # y[nans] = np.interp(x(nans), x(~nans), y[~nans])

        # Pandas Interpolation
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


body_parts = utils.get_body_parts()


# Recieves args from main (including video path) and params to configure the library
# Creates 3 csv files(all keypoints, valid and invalid ones) and emplace wire-frame.
def get_keypoints_csv_from_video(video_path, params):
    video_name = utils.get_file_name(video_path)
    video_name = utils.filename_without_suffix(video_name)
    output_dirs = utils.generate_dirs_for_output_of_movie(video_name)

    # Extract frames
    f.extract_frames_by_file(file=video_path, output=output_dirs['time_path'])

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
    opWrapper.configure(params)
    opWrapper.start()

    # Process Image
    datum = op.Datum()
    print("path is {}".format(video_path))
    cap = cv2.VideoCapture(video_path)
    valid_keypoints_df = pd.DataFrame(columns=['Frame Number'] + body_parts)
    invalid_keypoints_df = pd.DataFrame(columns=['Frame Number'] + body_parts)
    all_keypoints_df = pd.DataFrame(columns=['Frame Number'] + body_parts)
    frame_detected_df = pd.DataFrame(columns=['Frame Number', 'Detected'])
    frame_counter = 0
    all_keypoints_df_csv_path = ''
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
            all_keypoints_df_csv_path = output_dirs['analytical_data_path'] + "/all_keypoints.csv"
            all_keypoints_df.to_csv(all_keypoints_df_csv_path)
            current_detected_frame_array = [frame_counter, 0]
            current_detected_frame_df = pd.DataFrame(current_detected_frame_array).T
            current_detected_frame_df.columns = ['Frame Number', 'Detected']
            frame_detected_df = pd.concat([frame_detected_df, current_detected_frame_df], sort=False)
            frame_detected_df.to_csv(output_dirs['analytical_data_path'] + "/is_frame_detected.csv")

        # if not args[0].no_display:
        cv2.imshow("body from video", datum.cvOutputData)

        key = cv2.waitKey(1)

        frame_counter += 1

    # When everything done, release
    # the video capture object
    print("finished")
    cap.release()
    # Closes all the frames
    cv2.destroyAllWindows()

    return all_keypoints_df_csv_path


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