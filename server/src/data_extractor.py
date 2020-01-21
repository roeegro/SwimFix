# Edited by Roee Groiser and Tom Marzea
import math
import numpy as np
from numpy.linalg import norm
from scipy import interpolate

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
