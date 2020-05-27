# Edited by Roee Groiser and Tom Marzea

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import output_manager
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


def show_body_parts_location_by_time(output_dirs):
    all_keypoints_df = pd.read_csv(output_dirs['analytical_data_path'] + "/all_keypoints.csv")
    frame_axis = all_keypoints_df['Frame Number'].to_list()
    all_keypoints_df.drop(['Unnamed: 0', 'Frame Number'], axis='columns', inplace=True)
    body_triplets = [all_keypoints_df.columns[i:i + 3] for i in range(0, len(all_keypoints_df.columns), 3)]
    C = np.array([[0, 0, 0], [0, 255, 0], [0, 0, 0]])
    for triplet in body_triplets:
        x_coor = all_keypoints_df[triplet[0]].to_list()
        y_coor = all_keypoints_df[triplet[1]].to_list()
        score = all_keypoints_df[triplet[2]]
        coefficients_for_x_graph = np.polyfit(frame_axis, x_coor, 3)
        coefficients_for_y_graph = np.polyfit(frame_axis, y_coor, 3)
        poly_x = np.poly1d(coefficients_for_x_graph)
        poly_y = np.poly1d(coefficients_for_y_graph)
        frame_partition = np.linspace(frame_axis[0], frame_axis[-1], 0.1)
        new_x_coor = poly_x(frame_partition)
        new_y_coor = poly_y(frame_partition)
        plt.plot(frame_axis, x_coor, frame_partition, new_x_coor)
        plt.savefig(output_dirs['figures_path'] + "/{}_by_frame_and_accurancy".format(triplet[0]))
        plt.close()
        plt.plot(frame_axis, y_coor, frame_partition, new_y_coor)
        plt.savefig(output_dirs['figures_path'] + "/{}_by_frame_and_accurancy".format(triplet[1]))
        plt.close()

        # fig1 = plt.figure()
        # fig2 = plt.figure()
        # ax = fig1.add_subplot(111)
        # bx = fig2.add_subplot(111)
        # for i in range(len(frame_axis)):
        #     ax.scatter(frame_axis[i], x_coors[i], color='green')
        # fig1.savefig("../output/figures/{}_by_frame_and_accurancy".format(triplet[0]))
        # for i in range(len(frame_axis)):
        #     bx.scatter(frame_axis[i], x_coors[i], color = "green")
        # fig2.savefig("../output/figures/{}_by_frame_and_accurancy".format(triplet[1]))


def create_graph(csv_path, y_cols=None, x_col='Frame Number', mult_figures=True):
    output_path = output_manager.get_figures_dir()
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


def plot_frame_detection(csv_path, y_cols=None, mult_figures=True):
    output_path = output_manager.get_figures_dir()
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


def plot_histogram_from_dict(data_dicts, xlabel, ylabel, filename=None):
    output_path = output_manager.get_figures_dir()
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


def plot_scatter_from_dict(data_dict, xlabel, ylabel, filename=None):
    output_path = output_manager.get_figures_dir()
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


# Assumption : The shape of all asked dfs must be the same, and columns are the same.
def plot_multi_graphs_from_other_csvs(csv_paths, y_cols=None, x_col='Frame Number', mult_figures=True):
    figures_path = output_manager.get_figures_dir()
    # print('figures dir = {}'.format(figures_path))
    analytics_path = output_manager.get_analytics_dir()
    if csv_paths is str:
        create_graph(csv_paths, y_cols, x_col, mult_figures)
    else:
        dfs = [pd.read_csv(csv_path).set_index(x_col) for csv_path in csv_paths]
        x = dfs[0][x_col].values if x_col != 'Frame Number' else dfs[0].index
        if y_cols is None:
            y_cols = dfs[0].columns.difference([x_col]).values
        elif y_cols is str:
            y_cols = [y_cols]
        for y_col in y_cols:
            # print('y_col = {} '.format(y_col))

            fig, ax = plt.subplots()
            y_values = [df[y_col].values for df in dfs]
            # print('values of all ys in the same column = {}'.format(y_values))
            for index, y_value in enumerate(y_values):
                dict_for_df = {x_col: dfs[index][x_col].values if x_col != 'Frame Number' else dfs[index].index}
                # print('values of all ys in specific column = {}'.format(y_value))
                x_axis_of_current_csv = dfs[index][x_col] if x_col != 'Frame Number' else dfs[index].index
                x_y_as_series = pd.Series(index=x_axis_of_current_csv,data=y_value)
                # plt.plot(x, y_value)
                ax.plot(x_y_as_series,label=csv_paths[index].split('/')[-1])
                # print([y_col + ' from ' + csv_path for csv_path in csv_paths])
                # plt.legend([y_col + ' from ' + csv_path.split('/')[-1] for csv_path in csv_paths])
                dict_for_df.update({y_col + '_from_' + csv_paths[index].split('/')[-1]: y_value})
            legend = ax.legend(loc='best', fontsize='x-large')
            plt.xlabel(x_col)
            plt.ylabel('location in frame')
            plt.title("{} comparison".format(y_col))
            df_to_new_csv = pd.DataFrame(data=dict_for_df).set_index(x_col)
            df_to_new_csv.to_csv(analytics_path + "/{}_comparison.csv".format(y_col))
            plt.savefig(figures_path + "/{}_by_{}_comparison".format(y_col, x_col))
            plt.close()
