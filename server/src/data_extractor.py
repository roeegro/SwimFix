# Edited by Roee Groiser and Tom Marzea
import math
import numpy as np
from numpy.linalg import norm
import utils
import pandas as pd


def generate_vectors_csv(csv_path, outp_path='../output'):
    df = pd.read_csv(csv_path)
    df.reset_index(drop=True, inplace=True)
    vectors_df = pd.DataFrame(
        columns=['Frame Number', 'RChestX', 'RChestY', 'LChestX', 'LChestY', 'RArmX', 'RArmY', 'LArmX', 'LArmY',
                 'RForearmX', 'RForearmY', 'LForearmX', 'LForearmY'])
    kp_cols = sorted(filter(lambda name: 'Score' not in name, df.columns.values))
    df.drop(columns=df.columns.difference(kp_cols), axis=1, inplace=True)
    df.reset_index(drop=True, inplace=True)
    # frame_nums = df['Frame Number'].values
    df.drop(columns=['Unnamed: 0'], axis=1, inplace=True)
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
    outp_path += '/vectors.csv'
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


def generate_angles_csv(csv_path, outp_path='../output'):
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
    outp_path += '/angels.csv'
    pd.DataFrame.to_csv(angles_df, outp_path, index=False)
    return outp_path


def generate_is_detected_keypoint_csv(csv_path, score_cols=None, outp_path='../output'):
    df = pd.read_csv(csv_path)
    if score_cols is None:
        score_cols = list(filter(lambda x: 'Score' in x, df.columns.values))[1:]
        name = 'is_all_detected'
    else:
        name = '_'.join(score_cols)
        score_cols = list(map(utils.keypoint_to_score, score_cols))
    is_detected_cols = list(map(lambda x: x.replace('Score', ''), score_cols))
    path = outp_path + '/is_' + name + '_detected.csv'
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
