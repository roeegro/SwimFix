# Edited by Roee Groiser and Tom Marzea

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import output_manager
import cv2
import math
import utils


def show_avg_angle_diff(dict_of_avg_angle_for_test, dict_of_avg_angle_for_tested):
    labels = dict_of_avg_angle_for_test.keys()

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width / 2, dict_of_avg_angle_for_test.values(), width, label='Men')
    rects2 = ax.bar(x + width / 2, dict_of_avg_angle_for_tested.values(), width, label='Women')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Avg angle')
    ax.set_title('Body part')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()

    plt.show()


def create_graph(csv_path, y_cols=None, x_col='Frame Number', mult_figures=True, output_path=None):
    """ Creates graph from csv path and save the figures in output path.

    :param csv_path: Path to csv to derive figures from.
    :param y_cols: Columns to generate figures from.
    :param x_col: Column to be the x axis in figures.
    :param mult_figures: Plot multifigures flag.
    :param output_path: Path to save figures in.
    """
    output_path = output_manager.get_figures_dir() if output_path is None else output_path
    df = pd.read_csv(csv_path)
    df.reset_index(drop=True, inplace=True)
    x = df[x_col].values
    if y_cols is None:
        y_cols = df.columns.difference([x_col]).values
    elif y_cols is str:
        y_cols = [y_cols]
    for y_col in y_cols:
        y = df[y_col].values
        plt.plot(x, y)
        if mult_figures:
            plt.xlabel(x_col)
            plt.ylabel(y_col)
            plt.title = y_col + 'as a function of ' + x_col
            plt.savefig(output_path + "/{}_by_{}".format(y_col, x_col))
            plt.clf()
    if not mult_figures:
        plt.xlabel(x_col)
        plt.legend(y_cols)
        plt.savefig(output_path + "/{}_by_{}".format('_'.join(y_cols), x_col))
    plt.close()


def plot_frame_detection(csv_path, y_cols=None, mult_figures=True, output_path=None):
    output_path = output_manager.get_figures_dir() if output_path is None else output_path
    df = pd.read_csv(csv_path)
    df.reset_index(drop=True, inplace=True)
    frames = df['Frame Number'].values
    if y_cols is None:
        y_cols = df.columns.difference(['Frame Number', 'Unnamed: 0']).values
    for y_col in y_cols:
        y = df[y_col].values
        if not mult_figures:
            plt.scatter(frames, y, c='blue')
        if mult_figures:
            plt.scatter(frames, y)
            plt.xlabel('Frame Number')
            plt.ylabel(y_col)
            plt.title = y_col + 'Frame Detection'
            plt.savefig(output_path + '/{}_frame_detection'.format(y_col))
            plt.clf()
    if not mult_figures:
        plt.xlabel('Frame Number')
        plt.savefig(output_path + "/all_keypoints_frame_detection")
    plt.close()


def plot_histogram_from_dict(data_dicts, xlabel, ylabel, filename=None, output_path=None):
    output_path = output_manager.get_figures_dir() if output_path is None else output_path
    if filename is None:
        filename = ylabel + '_of_' + xlabel + '_histogram'
    if isinstance(data_dicts, dict) or len(data_dicts) == 1:
        rects = plt.bar(data_dicts.keys(), data_dicts.values())
        autolabel(rects, plt)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
    else:
        fig, ax = plt.subplots()
        for label, data_dict in [x.items() for x in data_dicts]:
            rects = ax.bar(data_dict.keys(), data_dict.values(), label=label)
            autolabel(rects, ax)
        ax.legend()
    plt.savefig(output_path + '/' + filename)
    plt.close()


def plot_scatter_from_dict(data_dict, xlabel, ylabel, filename=None, output_path=None):
    output_path = output_manager.get_figures_dir() if output_path is None else output_path
    plt.scatter(data_dict.keys(), data_dict.values())
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    for angle, val in data_dict.items():
        plt.annotate(round(val, 2), (angle, val))
    plt.savefig(output_path + '/' + filename)
    plt.close()


def autolabel(rects, ax):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


def plot_multi_graphs_from_other_csvs(csv_paths, y_cols=None, x_col='Frame Number', mult_figures=True,
                                      output_path=None,name_prefix = ''):
    """ Plot single or multi figures from different csv files.
        **Very important assumption** : The columns must be the same when using this function for more than one csv path.

    :param csv_paths: List of csv files paths to derive graphs from, or string if there is only 1 csv file.
    :param y_cols: Columns to compare
    :param x_col: x axis in the figures.
    :param mult_figures:
    :param output_path: Path to save figures in.
    """
    figures_path = output_manager.get_figures_dir() if output_path is None else output_path
    analytics_path = output_manager.get_analytics_dir() if output_path is None else output_path
    if type(csv_paths) is str:
        create_graph(csv_paths, y_cols, x_col, mult_figures)
    else:
        dfs = [pd.read_csv(csv_path).set_index(x_col) for csv_path in csv_paths]
        x = dfs[0][x_col].values if x_col != 'Frame Number' else dfs[0].index
        if y_cols is None:
            y_cols = dfs[0].columns.difference([x_col]).values
        elif y_cols is str:
            y_cols = [y_cols]
        for y_col in y_cols:
            fig, ax = plt.subplots()
            y_values = [df[y_col].values for df in dfs]
            dict_for_df = dict()
            dict_for_df.update(
                {x_col: dfs[0][x_col].values if x_col != 'Frame Number' else dfs[0].index})
            for index, y_value in enumerate(y_values):
                # if index == 0:
                #     dict_for_df.update(
                #         {x_col: dfs[index][x_col].values if x_col != 'Frame Number' else dfs[index].index})
                x_axis_of_current_csv = dfs[index][x_col] if x_col != 'Frame Number' else dfs[index].index
                np_nans = np.empty(len(dict_for_df[x_col]))
                np_nans[:] = np.nan
                x_y_as_series = pd.Series(index=dict_for_df[x_col], data=np_nans)
                x_y_as_series.update(pd.Series(data=y_value, index=x_axis_of_current_csv))
                ax.plot(x_y_as_series, label=csv_paths[index].split('/')[-1])
                dict_for_df.update({y_col + '_from_' + csv_paths[index].split('/')[-1]: x_y_as_series.values})
            legend = ax.legend(loc='best', fontsize='medium')
            plt.xlabel(x_col)
            plt.ylabel('location in frame')
            specific_y_col = y_col
            title = specific_y_col + ' comparison'
            plt.title = title
            df_to_new_csv = pd.DataFrame(data=dict_for_df).set_index(x_col)
            df_to_new_csv.to_csv(analytics_path + '/' + name_prefix + specific_y_col + '_comparison.csv')
            plt.savefig(figures_path + '/' + name_prefix + specific_y_col + '_by_' + x_col + '_comparison')
            plt.close(fig)


def draw_detected_keypoints(keypoints_path):
    keypoints_df = pd.read_csv(keypoints_path).set_index('Frame Number')
    # swimfix_frames_dir_path = os.getcwd() + '/../output/tom\MVI_8027_from_frame_60/2020-06-08/13-09-47/to_annotate'
    swimfix_frames_dir_path = output_manager.get_output_dir_path(key='swimfix_frames_path')
    coco_skeleton = utils.get_body_skeleton()
    for index, frame_data in keypoints_df.iterrows():
        int_index = int(index)
        # current_frame_path = swimfix_frames_dir_path + '/annotated_frame_{}.jpg'.format(int_index)
        current_frame_path = swimfix_frames_dir_path + '/swimfix_annotated_frame_{}.jpg'.format(int_index)
        current_frame = cv2.imread(current_frame_path)
        nose = (int(frame_data['NoseX']), int(frame_data['NoseY'])) if not math.isnan(frame_data['NoseX']) else (
            math.nan, math.nan)
        neck = (int(frame_data['NeckX']), int(frame_data['NeckY'])) if not math.isnan(frame_data['NeckX']) else (
            math.nan, math.nan)
        r_shoulder = (int(frame_data['RShoulderX']), int(frame_data['RShoulderY'])) if not math.isnan(
            frame_data['RShoulderX']) else (
            math.nan, math.nan)
        r_elbow = (int(frame_data['RElbowX']), int(frame_data['RElbowY'])) if not math.isnan(frame_data['RElbowX']) else (
            math.nan, math.nan)
        r_wrist = (int(frame_data['RWristX']), int(frame_data['RWristY'])) if not math.isnan(frame_data['RWristX']) else (
            math.nan, math.nan)
        l_shoulder = (int(frame_data['LShoulderX']), int(frame_data['LShoulderY'])) if not math.isnan(
            frame_data['LShoulderX']) else (
            math.nan, math.nan)
        l_elbow = (int(frame_data['LElbowX']), int(frame_data['LElbowY'])) if not math.isnan(frame_data['LElbowX']) else (
            math.nan, math.nan)
        l_wrist = (int(frame_data['LWristX']), int(frame_data['LWristY'])) if not math.isnan(frame_data['LWristX']) else (
            math.nan, math.nan)
        body_parts = [nose, neck, r_shoulder, r_elbow, r_wrist, l_shoulder, l_elbow, l_wrist]

        for body_part in body_parts:
            if not math.isnan(body_part[0]):
                current_frame = cv2.circle(current_frame, body_part, 2, (0, 0, 0), 5)
        for line in coco_skeleton:
            from_body_part_index = line[0]
            to_body_part_index = line[1]
            from_point = body_parts[from_body_part_index]
            to_point = body_parts[to_body_part_index]
            if math.isnan(from_point[0]) or math.isnan(to_point[0]):
                continue
            current_frame = cv2.line(current_frame, from_point, to_point, (0, 255, 0), 4)
            cv2.imwrite(current_frame_path,current_frame)


if __name__ == '__main__':
    import os

    draw_detected_keypoints(os.getcwd() + '/interpolated_and_filtered_all_keypoints.csv')
