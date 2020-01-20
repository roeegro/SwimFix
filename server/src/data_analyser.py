# Edited by Roee Groiser and Tom Marzea
from main import *
import numpy as np
from scipy import interpolate
from scipy.signal import argrelextrema, argrelmin

def create_interpolated_csv(csv_path, y_cols, x_col='Frame Number', output_path='output'):
    df = pd.read_csv(csv_path)
    if type(y_cols) == str:
        y_cols = [y_cols]
    cols = y_cols + [x_col]
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
        df = df[df.columns.dropna()]
        df[col_name].interpolate(method='cubic', inplace=True)

        y = df[col_name].values
        x = df['Frame Number'].values
        xnew = np.linspace(x.min(), x.max(), len(x))
        bspline = interpolate.make_interp_spline(x, y)
        y_smoothed = bspline(xnew)
        df[col_name] = y_smoothed

    path = output_path + '/' + '_'.join(y_cols) + '.csv'
    df.to_csv(path)
    return path


def calc_avg_period(csv_path, col_names, min_period=1.5, frame_rate=30, maximum=True, avg=False):
    df = pd.read_csv(csv_path)
    all_keypoints_csv_path = '../../all_keypoints.csv'
    all_df = pd.read_csv(all_keypoints_csv_path)
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
        l = list(map(lambda x: x[1], avg_per_dict.values()))
        return round(np.average(l), 3)
    else:
        return avg_per_dict

# def get_confidence_score(csv_path, frames):
#     df = pd.read_csv(csv_path)
