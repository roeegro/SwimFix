# Edited by Roee Groiser and Tom Marzea
import numpy as np
from scipy.signal import argrelextrema, argrelmin
import pandas as pd


def calc_avg_period(csv_path, col_names=None, min_period=1.5, frame_rate=30, maximum=True):
    """ Calculate averagem period time from csv_path which contains all key points.

    :param csv_path: Path to all key points csv file.
    :param col_names: Columns to calculate by the avg period.
    :param min_period: Minimum period time to consider it as a period time.
    :param frame_rate: Frame rate of image to calculate time period in seconds
    :param maximum:
    :return: Average time period per body part.
    """
    if col_names is None:
        col_names = ['RWristY', 'LWristY']
    df = pd.read_csv(csv_path)
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
    return avg_per_dict


def calc_avg_angle(csv_path, col_names=None):
    """ Returns dictionary of average angle per body part."""
    df = pd.read_csv(csv_path)
    if col_names is None:
        col_names = df.columns.difference(['Frame Number', 'Unnamed: 0']).values
    # df.drop(columns=df.columns.differecne(col_names), index=1, inplace=True)
    avg_angle_dict = {}
    for col in col_names:
        avg_angle_dict[col] = df[col].mean()
    return avg_angle_dict


def calc_detected_frames_count_from_csv(detected_frames_csv_path, keypoints=None, with_acc=False):
    """ Calculate what is the percentage of time that body part was detected."""
    df = pd.read_csv(detected_frames_csv_path)
    if keypoints is None:
        keypoints = df.columns.difference(['Frame Number', 'Unnamed: 0']).values
    det_frame_count_dict = dict()
    total_frames = len(df['Frame Number'])
    for keypoint in keypoints:
        total_detected = df[keypoint].sum()
        det_frame_count_dict[keypoint] = {'Total detected': total_detected}
        if with_acc:
            acc = round(total_detected / total_frames, 3)
            det_frame_count_dict[keypoint]['Accuracy'] = acc
    if not with_acc:
        for key, value in det_frame_count_dict.items():
            det_frame_count_dict[key] = value['Total detected']
    return det_frame_count_dict
