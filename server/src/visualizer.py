# Edited by Roee Groiser
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import utils

def create_all_figures(output_dirs):
    show_figures_of_angles_by_time(output_dirs)
    show_frame_detected_figure(output_dirs)
    show_body_parts_by_frame(output_dirs)
    show_body_parts_location_by_time(output_dirs);


def show_frame_detected_figure(output_dirs):
    frame_df = pd.read_csv(output_dirs['analytical_data_path'] + '/is_frame_detected.csv')
    x = frame_df['Frame Number']
    y = []
    for index, row in frame_df.iterrows():
        if row['Detected']:
            y.extend([1])
        else:
            y.extend([0])
    plt.xlabel('Frame Number')
    plt.ylabel('valid frame')
    plt.plot(x, y, 'ro', color='green')
    plt.savefig(output_dirs['figures_path'] + "/detected_frames_figure")
    plt.close()


def show_figures_of_angles_by_time(output_dirs):
    angles_df = pd.read_csv(output_dirs['analytical_data_path'] + '/angles_by_time.csv')
    columns = angles_df.columns
    for col in columns:
        if col == "Frame Number":
            continue
        x = angles_df['Frame Number']
        y = angles_df[col]
        plt.xlabel('Frame number')
        plt.ylabel("{} angle".format(col))
        plt.plot(x, y)
        plt.savefig(output_dirs['figures_path'] + "/{}_angle__by_frame".format(col))
        plt.close()


def show_body_parts_by_frame(output_dirs):
    df = pd.read_csv(
        output_dirs['analytical_data_path'] + "/body_part_detected_by_frame_df.csv")
    x = df['Frame Number']
    for col in df.columns:
        if col == "Frame Number":
            continue
        y = df[col]
        plt.ylabel("Detected " + col)
        plt.plot(x, y, 'ro')
        plt.savefig(output_dirs['figures_path'] + '/{}_detected_by_frame'.format(col))
        plt.close()


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
    output_path = utils.get_figures_dir()
    df = pd.read_csv(csv_path)
    df.reset_index(drop=True, inplace=True)
    x = df[x_col].values
    if y_cols is None:
        y_cols = df.columns.difference([x_col, 'Unnamed: 0']).values
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
    output_path = utils.get_figures_dir()
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


def plot_histogram_from_dict(data_dict):
    output_path = utils.get_figures_dir()
    # print(data_dict.keys())
    plt.bar(data_dict.keys(), data_dict.values())
    plt.xlabel('Keypoints')
    plt.ylabel('No. of detected frames')
    plt.savefig(output_path + '/detected_frames_by_keypoints_histogram')
    plt.close()


# def plot_all_figures()