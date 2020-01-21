# Edited by Roee Groiser and Tom Marzea
import numpy as np
from scipy.signal import argrelextrema, argrelmin
import pandas as pd


def calc_avg_period(csv_path, col_names=None, min_period=1.5, frame_rate=30, maximum=True, avg=True):
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
    if len(avg_per_dict) == 1:
        return avg_per_dict[col_names[0]][1]
    elif avg:
        avg_list = list(map(lambda x: x[1], avg_per_dict.values()))
        return round(np.average(avg_list), 3)
    else:
        return avg_per_dict


def calc_avg_angle(csv_path, col_names=None):
    df = pd.read_csv(csv_path)
    if col_names is None:
        col_names = df.columns.difference(['Frame Number', 'Unnamed: 0']).values
    # df.drop(columns=df.columns.differecne(col_names), index=1, inplace=True)
    avg_angle_dict = {}
    for col in col_names:
        avg_angle_dict[col] = df[col].mean()
    return avg_angle_dict
