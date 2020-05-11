import math
import shutil
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QTableWidgetItem
import tkinter as tk
from tkinter import filedialog
import filetype
import os
import cv2
import pandas as pd
from pip._vendor.pkg_resources import parse_requirements


class GuiData():
    frames_number = 10  # Just an initial frame_number. Updated at runtime.
    lines = list()
    dlg = None
    curr_measured_body_part_index = 0
    video_path = None
    all_keypoints_csv_path = None
    frames_for_final_video = list()
    are_keypoints_known = False
    stabbed_points_per_frame = list()
    original_frames = list()
    resolution_ratio = (0, 0)
    selected_item_val = None


def run():
    app = QtWidgets.QApplication([])
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    gui_setup()
    # show and exec
    app.aboutToQuit.connect(red_btn_pressed)
    app.exec()


def gui_setup():
    dlg = uic.loadUi('test_generator.ui')
    GuiData.dlg = dlg
    get_from_keypoint_cmbox().setEnabled(False)
    get_to_keypoint_cmbox().setEnabled(False)
    get_next_button().setEnabled(False)
    get_prev_button().setEnabled(False)
    get_lines_tbl().setEnabled(False)
    get_finish_line_def_btn().setEnabled(False)
    get_add_line_btn().setEnabled(False)
    get_insert_row_btn().setEnabled(False)
    get_finish_body_parts_def_btn().setEnabled(False)
    get_set_default_setting_btn().setEnabled(False)
    get_undo_btn().setEnabled(False)
    get_load_csv_btn().setEnabled(False)
    get_clean_all_btn().setEnabled(False)

    get_current_frame_label().setText(str(0))
    get_image_label().setScaledContents(True)

    # Build body part table
    body_coors_tbl = get_body_coors_tbl()
    body_coors_tbl.setColumnCount(3)  # For x and y only
    body_coors_tbl.setRowCount(0)
    body_coors_tbl.setHorizontalHeaderItem(0, QTableWidgetItem('Body Part Name'))
    body_coors_tbl.setHorizontalHeaderItem(1, QTableWidgetItem('X'))
    body_coors_tbl.setHorizontalHeaderItem(2, QTableWidgetItem('Y'))
    # Build line table
    line_tbl = get_lines_tbl()
    line_tbl.setColumnCount(2)
    line_tbl.setRowCount(0)
    line_tbl.setHorizontalHeaderItem(0, QTableWidgetItem('From'))
    line_tbl.setHorizontalHeaderItem(1, QTableWidgetItem('To'))

    # button event binds
    get_load_video_btn().clicked.connect(load_video_btn_pressed)
    get_insert_row_btn().clicked.connect(lambda: body_coors_tbl.setRowCount(body_coors_tbl.rowCount() + 1))
    get_finish_body_parts_def_btn().clicked.connect(finish_define_table_btn_pressed)
    get_finish_line_def_btn().clicked.connect(finish_line_def_btn_pressed)
    get_next_button().clicked.connect(next_btn_pressed)
    get_prev_button().clicked.connect(prev_btn_pressed)
    get_from_keypoint_cmbox().currentIndexChanged.connect(on_select_from_keypoint)
    get_add_line_btn().clicked.connect(add_line_btn_pressed)
    get_set_default_setting_btn().clicked.connect(set_default_setting_btn_pressed)
    get_undo_btn().clicked.connect(undo_btn_pressed)
    get_load_csv_btn().clicked.connect(load_csv_btn_pressed)
    get_clean_all_btn().clicked.connect(clean_all_btn_pressed)
    # Window settings

    dlg.showMaximized()
    dlg.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.CustomizeWindowHint)

    dlg.setGeometry(0, 0, dlg.width(), dlg.height())
    dlg.setFixedSize(dlg.width(), dlg.height())
    dlg.show()


# Events

def add_line_btn_pressed():
    lines_tbl = get_lines_tbl()
    from_keypoint = get_from_keypoint_cmbox().currentText()
    curr_line = lines_tbl.rowCount()
    lines_tbl.setRowCount(curr_line + 1)
    lines_tbl.setItem(curr_line, 0, QTableWidgetItem(str(from_keypoint)))
    to_keypoint = get_to_keypoint_cmbox().currentText()
    if len(to_keypoint) == 0:
        lines_tbl.setItem(curr_line, 1, QTableWidgetItem(str(from_keypoint)))
    else:
        lines_tbl.setItem(curr_line, 1, QTableWidgetItem(str(to_keypoint)))


def body_part_tbl_cell_selected(item):
    GuiData.curr_measured_body_part_index = item.row()
    print(item.text())


def clean_all_btn_pressed():
    clean_body_parts_coors_tbl()
    current_frame = int(get_current_frame_label().text())
    GuiData.stabbed_points_per_frame[current_frame] = dict()  # reset stabbed points dict
    edit_shown_frame()
    GuiData.curr_measured_body_part_index = 0


def clean_body_parts_coors_tbl():
    body_parts_tbl = get_body_coors_tbl()
    for row in range(0, body_parts_tbl.rowCount()):
        body_parts_tbl.setItem(row, 1, QTableWidgetItem(str(math.nan)))  # X Col
        body_parts_tbl.setItem(row, 2, QTableWidgetItem(str(math.nan)))  # Y col


def clean_lines_tbl():
    lines_tbl = get_lines_tbl()
    for row in range(0, lines_tbl.rowCount()):
        lines_tbl.setItem(row, 1, QTableWidgetItem(str(math.nan)))  # from Col
        lines_tbl.setItem(row, 2, QTableWidgetItem(str(math.nan)))  # to col


def clicked_coor_into_tbl(event):
    x = math.floor(
        event.pos().x() / GuiData.resolution_ratio[0])  # match the selected point's coors to match to image resolution
    y = math.floor(event.pos().y() / GuiData.resolution_ratio[1])
    print('width ratio is {}'.format(GuiData.resolution_ratio[0]))
    print('width ratio is {}'.format(GuiData.resolution_ratio[1]))
    body_part_tbl = get_body_coors_tbl()
    row_index_in_body_part_tbl = GuiData.curr_measured_body_part_index
    if body_part_tbl.rowCount() <= row_index_in_body_part_tbl:
        return
    body_part_tbl.setItem(row_index_in_body_part_tbl, 1, QTableWidgetItem(str(x)))
    body_part_tbl.setItem(row_index_in_body_part_tbl, 2, QTableWidgetItem(str(y)))
    # update shown frame
    curr_frame = int(get_current_frame_label().text())
    body_part_name = body_part_tbl.item(row_index_in_body_part_tbl, 0).text()
    GuiData.stabbed_points_per_frame[curr_frame][body_part_name] = (x, y)
    edit_shown_frame()
    GuiData.curr_measured_body_part_index += 1


def finish_define_table_btn_pressed():
    body_coors_tbl = get_body_coors_tbl()
    body_coors_tbl.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
    get_insert_row_btn().setEnabled(False)
    get_finish_body_parts_def_btn().setEnabled(False)
    get_lines_tbl().setEnabled(True)
    get_finish_line_def_btn().setEnabled(True)
    get_add_line_btn().setEnabled(True)

    from_keypoint_cmobx = get_from_keypoint_cmbox()
    vertical_headers = list()
    row_index = 0
    while row_index < body_coors_tbl.rowCount():
        try:
            to_add = str(body_coors_tbl.item(row_index, 0).text())
            if not to_add in vertical_headers:
                vertical_headers.append(to_add)
                row_index += 1
            else:
                body_coors_tbl.removeRow(row_index)
        except:
            body_coors_tbl.removeRow(row_index)
    from_keypoint_cmobx.addItems(vertical_headers)
    from_keypoint_cmobx.setEnabled(True)


def finish_line_def_btn_pressed():
    lines_tbl = get_lines_tbl()
    body_part_coors_tbl = get_body_coors_tbl()
    # take each record (line) and store it in the list
    for row in range(0, lines_tbl.rowCount()):
        from_keypoint = lines_tbl.item(row, 0).text()
        to_keypoint = lines_tbl.item(row, 1).text()
        if not (to_keypoint, from_keypoint) in GuiData.lines:
            line_as_tuple = (from_keypoint, to_keypoint)
            GuiData.lines.append(line_as_tuple)

    get_next_button().setEnabled(True)
    get_prev_button().setEnabled(True)
    get_undo_btn().setEnabled(True)
    get_clean_all_btn().setEnabled(True)
    get_add_line_btn().setEnabled(False)
    get_to_keypoint_cmbox().setEnabled(False)
    get_from_keypoint_cmbox().setEnabled(False)
    get_load_csv_btn().setEnabled(False)
    # Enables the user to select specific body part when annotate points on the screen
    get_body_coors_tbl().itemClicked.connect(body_part_tbl_cell_selected)

    create_csv()
    frame_path = get_frame(0)
    pixmap = QPixmap(frame_path)
    pixmap_height = pixmap.height()
    pixmap_width = pixmap.width()

    # img = cv2.imread(frame_path)
    # height = img.shape[0]
    # width = img.shape[1]
    image_label = get_image_label()
    # image_label.setFixedSize(height, width)
    image_label.setPixmap(pixmap)
    image_label.mousePressEvent = clicked_coor_into_tbl

    # Fill the table with nones for first frame
    for row in range(body_part_coors_tbl.rowCount()):
        for col in range(1, body_part_coors_tbl.columnCount()):
            body_part_coors_tbl.setItem(row, col, QTableWidgetItem(str(math.nan)))

    # Draw circles and lines based on the known data if exist
    if GuiData.are_keypoints_known is True:
        paint_for_all_frames()
    build_keypoints_tbl_for_request_frame(0)


def insert_body_part_btn_pressed():
    body_coors_tbl = get_body_coors_tbl()
    actual_row_count = body_coors_tbl.rowCount() + 1
    body_coors_tbl.setRowCount(actual_row_count)


def load_csv_btn_pressed():
    root = tk.Tk()
    root.withdraw()
    keypoints_tbl = get_body_coors_tbl()
    file_path = filedialog.askopenfilename()
    try:
        df = pd.read_csv(file_path)  # Try read csv by load it to df
        GuiData.all_keypoints_csv_path = file_path
        # Load cols into keypoints tbl
        body_parts_with_axis_annotation = df.columns.to_list()[
                                          1::2]  # take cols without 'frame number' and without duplicates
        body_parts = [element[:len(element) - 1] for element in body_parts_with_axis_annotation]
        for i in range(len(body_parts)):
            keypoints_tbl.setRowCount(i + 1)
            keypoints_tbl.setItem(i, 0, QTableWidgetItem(str(body_parts[i])))

        # Set tables and buttons permissions.
        get_lines_tbl().setEnabled(False)
        get_insert_row_btn().setEnabled(False)
        get_finish_body_parts_def_btn().setEnabled(False)
        finish_define_table_btn_pressed()  # for setting lines between body parts.
        GuiData.are_keypoints_known = True
    except:
        get_msg_lbl().setText("Try select a video file")


def load_video_btn_pressed():
    root = tk.Tk()
    root.withdraw()

    while True:
        file_path = filedialog.askopenfilename()
        try:
            get_msg_lbl().setText("Trying generating frames")
            kind = filetype.guess(file_path)
            if str(kind.mime).split('/')[0] == 'video':
                GuiData.video_path = file_path
                GuiData.frames_number = generate_frames_from_video(file_path)
                get_msg_lbl().setText("Generation succeeded")
                gui_setup()
                get_insert_row_btn().setEnabled(True)
                get_finish_body_parts_def_btn().setEnabled(True)
                get_set_default_setting_btn().setEnabled(True)
                get_load_csv_btn().setEnabled(True)
                get_current_frame_label().setText(str(0))
                break
            # else:
            # get_msg_lbl().setText("Try select another video")
        except:
            get_msg_lbl().setText("Try select a video file")
            break


def next_btn_pressed():
    dlg = GuiData.dlg
    frames_number = GuiData.frames_number
    prev_frame_number = int(dlg.current_frame_number.text())
    current_frame_number = int(prev_frame_number) + 1
    current_frame_label = get_current_frame_label()
    current_frame_label.setText(str(current_frame_number))
    if current_frame_number < frames_number:
        frame_path = get_frame(current_frame_number)
        pixmap = QPixmap(frame_path)
        pixmap_height = pixmap.height()
        pixmap_width = pixmap.width()
        image_label = get_image_label()
        # image_label.setFixedSize(pixmap_width, pixmap_height)
        image_label.setPixmap(pixmap)
        image_label.mousePressEvent = clicked_coor_into_tbl
        # Update table of body parts to be ready for the next frame
        GuiData.curr_measured_body_part_index = 0
        save_coors_in_csv(prev_frame_number)
        draw_lines_by_tbl(int(prev_frame_number))
        build_keypoints_tbl_for_request_frame(current_frame_number)
        edit_shown_frame()
    else:
        red_btn_pressed()


def on_select_from_keypoint():
    selected_text = get_from_keypoint_cmbox().currentText()
    from_keypoint_cmbox = get_from_keypoint_cmbox()
    items = [from_keypoint_cmbox.itemText(i) for i in range(from_keypoint_cmbox.count())]
    items.remove(selected_text)
    get_to_keypoint_cmbox().clear()
    get_to_keypoint_cmbox().addItems(items)
    get_to_keypoint_cmbox().setEnabled(True)


def prev_btn_pressed():
    dlg = GuiData.dlg
    current_frame_number = int(dlg.current_frame_number.text())
    prev_frame_number = current_frame_number - 1
    current_frame_label = get_current_frame_label()
    if current_frame_number > 0:
        frame_path = get_frame(prev_frame_number)
        pixmap = QPixmap(frame_path)
        pixmap_height = pixmap.height()
        pixmap_width = pixmap.width()
        image_label = get_image_label()
        # image_label.setFixedSize(pixmap_width, pixmap_height)
        image_label.setPixmap(pixmap)
        image_label.mousePressEvent = clicked_coor_into_tbl
        # Update table of body parts to be ready for the next frame
        GuiData.curr_measured_body_part_index = 0
        current_frame_label.setText(str(prev_frame_number))
        save_coors_in_csv(current_frame_number)
        build_keypoints_tbl_for_request_frame(prev_frame_number)
        edit_shown_frame()


def red_btn_pressed():
    try:
        delete_frames_folder()
        output_video_name = create_video()
        csv_name = get_video_name() + "_expected.csv"
        add_data_to_excepted_csvs(output_video_name, csv_name)
    finally:
        return


def reset_guidata_object():
    GuiData.frames_number = 10  # Just an initial frame_number. Updated at runtime.
    GuiData.lines = list()
    GuiData.curr_measured_body_part_index = 0
    GuiData.video_path = None
    GuiData.all_keypoints_csv_path = None
    GuiData.frames_for_final_video = list()
    GuiData.are_keypoints_known = False
    GuiData.stabbed_points_per_frame = list()
    GuiData.original_frames = list()


def set_default_setting_btn_pressed():
    body_coors_tbl = get_body_coors_tbl()
    lines_tbl = get_lines_tbl()
    body_parts = get_body_parts()
    row_counter = 0
    for i in range(len(body_parts)):
        body_coors_tbl.setRowCount(i + 1)
        body_coors_tbl.setItem(i, 0, QTableWidgetItem(body_parts[i]))

    for i in range(0, 4):  # Just right side.
        lines_tbl.setRowCount(row_counter + 1)
        lines_tbl.setItem(row_counter, 0, QTableWidgetItem(body_parts[i]))
        lines_tbl.setItem(row_counter, 1, QTableWidgetItem(body_parts[i + 1]))
        row_counter += 1

    for i in range(5, len(body_parts) - 1):  # Just left side.
        lines_tbl.setRowCount(row_counter + 1)
        lines_tbl.setItem(row_counter, 0, QTableWidgetItem(body_parts[i]))
        lines_tbl.setItem(row_counter, 1, QTableWidgetItem(body_parts[i + 1]))
        row_counter += 1

    # connect left shoulder with chest
    lines_tbl.setRowCount(row_counter + 1)
    lines_tbl.setItem(row_counter, 0, QTableWidgetItem(body_parts[1]))
    lines_tbl.setItem(row_counter, 1, QTableWidgetItem(body_parts[5]))
    row_counter += 1

    finish_line_def_btn_pressed()
    get_next_button().setEnabled(True)
    get_prev_button().setEnabled(True)
    get_insert_row_btn().setEnabled(False)
    get_finish_body_parts_def_btn().setEnabled(False)
    get_finish_line_def_btn().setEnabled(False)
    get_set_default_setting_btn().setEnabled(False)


def undo_btn_pressed():
    curr_row = 0  # for a case that no row was selected
    if GuiData.curr_measured_body_part_index > 0:
        curr_row = GuiData.curr_measured_body_part_index
    body_parts_coor_tbl = get_body_coors_tbl()
    for col in range(1, body_parts_coor_tbl.columnCount()):
        body_parts_coor_tbl.setItem(curr_row, col, QTableWidgetItem(str(math.nan)))
    # Update shown frame
    try:
        body_part = str(body_parts_coor_tbl.item(curr_row, 0).text())
        stabbed_points_dict = GuiData.stabbed_points_per_frame[int(get_current_frame_label().text())]
        del stabbed_points_dict[body_part]
        edit_shown_frame()
    except:
        return


# Helpers
def add_data_to_excepted_csvs(output_video_name, csv_name):
    shutil.move(os.getcwd() + '/' + output_video_name, '../../server/excepted_data/videos')
    shutil.move(os.getcwd() + '/' + csv_name, '../../server/excepted_data/csvs')


def build_keypoints_tbl_for_request_frame(requested_frame_number):
    body_coors_tbl = get_body_coors_tbl()
    csv_path = get_all_keypoints_csv_path()
    keypoints_df = pd.read_csv(csv_path)
    rows = keypoints_df.shape[0]
    if requested_frame_number == rows:
        clean_body_parts_coors_tbl()
    else:
        prev_frame_df = keypoints_df.iloc[requested_frame_number, 1::]  # without the frame number column.
        coors = prev_frame_df.values.tolist()
        for i in range(0, len(coors)):
            if math.isnan(coors[i]):
                body_coors_tbl.setItem(i / 2, 1 + (i % 2), QTableWidgetItem(str(math.nan)))
            else:
                body_coors_tbl.setItem(i / 2, 1 + (i % 2), QTableWidgetItem(str((int(coors[i])))))


def create_csv():
    video_name = get_video_name()
    if not GuiData.all_keypoints_csv_path is None:  # There is an existing csv to copy from
        # copy the selected one to cwd
        original_csv_as_df = pd.read_csv(GuiData.all_keypoints_csv_path)
        csv_path = os.getcwd() + "\\" + video_name + "_expected.csv"
        original_csv_as_df.to_csv(csv_path, index=False)
        GuiData.all_keypoints_csv_path = csv_path  # keep it for write every frame keypoints coordinates.
        return
    body_parts_coors_tbl = get_body_coors_tbl()
    body_parts = list()
    body_parts.append('Frame Number')
    for row in range(0, body_parts_coors_tbl.rowCount()):
        for col in range(1, body_parts_coors_tbl.columnCount()):
            try:
                body_part = str(body_parts_coors_tbl.item(row, 0).text())
                axis = body_parts_coors_tbl.horizontalHeaderItem(col).text()
                body_parts.append(body_part + axis)
            except:
                continue
    df = pd.DataFrame(columns=body_parts)
    csv_path = os.getcwd() + "\\" + video_name + "_expected.csv"
    df.to_csv(csv_path, index=False)
    GuiData.all_keypoints_csv_path = csv_path  # keep it for write every frame keypoints coordinates.


def create_video():
    if len(GuiData.frames_for_final_video) == 0:
        return
    first_img = GuiData.frames_for_final_video[0]
    height, width, _ = first_img.shape
    size = (width, height)
    out = cv2.VideoWriter('{}.avi'.format(get_video_name()), cv2.VideoWriter_fourcc(*'DIVX'), 30, size)
    for i in range(len(GuiData.frames_for_final_video)):
        out.write(GuiData.frames_for_final_video[i])
    out.release()
    return '{}.avi'.format(get_video_name())


def delete_frames_folder():
    folder = get_frame_dir()
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        shutil.rmtree(get_frame_dir())


def draw_lines_by_tbl(edited_frame_number):
    try:
        img_path = get_frame(edited_frame_number)
        image = cv2.imread(img_path)
        color = (0, 250, 0)
        thickness = 1
        for tuple in GuiData.lines:
            from_keypoint = tuple[0]
            to_keypoint = tuple[1]
            try:
                x_from, y_from = pixel_coor_by_keypoint(from_keypoint)
                x_to, y_to = pixel_coor_by_keypoint(to_keypoint)
            except:
                continue
            from_point = (x_from, y_from)
            to_point = (x_to, y_to)
            image = cv2.line(image, from_point, to_point, color, thickness)
            image = cv2.circle(image, (x_from, y_from), 2, color, 2)
            image = cv2.circle(image, (x_to, y_to), 2, color, 2)
        GuiData.frames_for_final_video[edited_frame_number] = image
    except Exception as e:
        print(e)


def generate_frames_from_video(video_path):
    vidcap = cv2.VideoCapture(video_path)
    img_label = get_image_label()
    img_label_size = img_label.size()
    frame_label_width = img_label_size.width()
    frame_label_height = img_label_size.height()
    if not os.path.exists("frames"):
        os.makedirs("frames")

    success, image = vidcap.read()
    count = 0
    while True:
        success, image = vidcap.read()
        if success is False:
            break
        height, width, _ = image.shape
        GuiData.resolution_ratio = (frame_label_width / width, frame_label_height / height)
        cv2.imwrite(get_frame_dir() + "\\frame_%d.jpg" % count, image)  # save frame as JPEG file
        GuiData.frames_for_final_video.append(image)
        GuiData.original_frames.append(image)
        GuiData.stabbed_points_per_frame.append(dict())
        count += 1
    return count - 1


def edit_shown_frame():
    curr_frame = int(get_current_frame_label().text())
    shown_frame = GuiData.original_frames[curr_frame].copy()
    color = (0, 250, 0)
    thickness = 1
    body_parts_coors_tbl = get_body_coors_tbl()
    stabbed_points_for_this_frame = GuiData.stabbed_points_per_frame[curr_frame]
    # Update the dictionary of stabbed points for a case that information is
    # already known (We used Load csv btn) and we want to show the existing points on the shown frame
    for row in range(body_parts_coors_tbl.rowCount()):
        try:
            x = int(body_parts_coors_tbl.item(row, 1).text())
            y = int(body_parts_coors_tbl.item(row, 2).text())
            body_part = body_parts_coors_tbl.item(row, 0).text()
            stabbed_points_for_this_frame[body_part] = (x, y)
        except:
            continue

    # locate points
    for key in GuiData.stabbed_points_per_frame[curr_frame].keys():
        coors = GuiData.stabbed_points_per_frame[curr_frame][key]
        shown_frame = cv2.circle(shown_frame, coors, 2, color, 2)
    # locate lines
    for tuple in GuiData.lines:
        from_keypoint = tuple[0]
        to_keypoint = tuple[1]
        try:
            from_point = GuiData.stabbed_points_per_frame[curr_frame][from_keypoint]
            to_point = GuiData.stabbed_points_per_frame[curr_frame][to_keypoint]
            shown_frame = cv2.line(shown_frame, from_point, to_point, color, thickness)
        except:
            continue

    # show edited frame
    height, width, channel = shown_frame.shape
    bytes_per_line = 3 * width
    q_img = QImage(shown_frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
    pixmap = QPixmap.fromImage(q_img)
    image_label = get_image_label()
    image_label.setPixmap(pixmap)


def paint_for_all_frames():
    all_keypoints_df = pd.read_csv(GuiData.all_keypoints_csv_path)
    frames_number = len(all_keypoints_df.index)
    for frame in range(0, frames_number):
        build_keypoints_tbl_for_request_frame(frame)
        draw_lines_by_tbl(frame)
        edit_shown_frame()


def pixel_coor_by_keypoint(keypoint_name):
    body_coors_tbl = get_body_coors_tbl()
    for row in range(0, body_coors_tbl.rowCount()):
        if body_coors_tbl.item(row, 0).text() == keypoint_name:
            break
    x_coor = int(body_coors_tbl.item(row, 1).text())
    y_coor = int(body_coors_tbl.item(row, 2).text())
    return x_coor, y_coor


def save_coors_in_csv(curr_frame_number):
    csv_path = get_all_keypoints_csv_path()
    all_frames_df = pd.read_csv(csv_path)
    df_cols = all_frames_df.columns.to_list()
    body_coors_tbl = get_body_coors_tbl()
    coors = list()
    coors.append(int(curr_frame_number))
    # for each body part
    for row in range(0, body_coors_tbl.rowCount()):
        # for each axis (first col is the name of the body part in table)
        for col in range(1, body_coors_tbl.columnCount()):
            try:
                item = body_coors_tbl.item(row, col).text()
                coors.append(int(item))
            except:
                coors.append(math.nan)
    current_frame_df = pd.DataFrame(coors).T
    current_frame_df.columns = df_cols
    if all_frames_df.empty:
        current_frame_df.to_csv(csv_path, index=False)
    else:
        rows = all_frames_df.shape[0]
        if rows == curr_frame_number:
            all_frames_df = pd.concat([all_frames_df, current_frame_df])
            all_frames_df.to_csv(csv_path, index=False)
        else:
            prev_frames_df = all_frames_df[:curr_frame_number]
            next_frames_df = all_frames_df[curr_frame_number + 1:]
            all_frames_df = pd.concat([prev_frames_df, current_frame_df, next_frames_df])
            all_frames_df.to_csv(csv_path, index=False)


# Getters
def get_add_line_btn():
    return GuiData.dlg.add_line_btn


def get_all_keypoints_csv_path():
    return GuiData.all_keypoints_csv_path


def get_body_parts():
    return ['Neck', 'Chest', 'RShoulder', 'RElbow', 'RWrist', 'LShoulder', 'LElbow', 'LWrist']


def get_body_coors_tbl():
    return GuiData.dlg.body_part_coors


def get_current_frame_label():
    return GuiData.dlg.current_frame_number


def get_clean_all_btn():
    return GuiData.dlg.clean_all_btn


def get_finish_body_parts_def_btn():
    return GuiData.dlg.finish_body_parts_def_btn


def get_finish_line_def_btn():
    return GuiData.dlg.finish_line_def_btn


def get_frame(curr_frame):
    frame_path = get_frame_dir() + '\\frame_{}.jpg'.format(curr_frame)
    return frame_path


def get_frame_dir():
    return os.getcwd() + '\\frames'


def get_from_keypoint_cmbox():
    return GuiData.dlg.from_keypoint_cmbox


def get_image_label():
    return GuiData.dlg.image_label


def get_insert_row_btn():
    return GuiData.dlg.insert_row_btn


def get_lines_tbl():
    return GuiData.dlg.lines_tbl


def get_load_csv_btn():
    return GuiData.dlg.load_csv_btn


def get_load_video_btn():
    return GuiData.dlg.load_video_btn


def get_msg_lbl():
    return GuiData.dlg.msg_lbl


def get_next_button():
    return GuiData.dlg.next_button


def get_prev_button():
    return GuiData.dlg.prev_button


def get_undo_btn():
    return GuiData.dlg.undo_btn


def get_set_default_setting_btn():
    return GuiData.dlg.set_default_setting_btn


def get_to_keypoint_cmbox():
    return GuiData.dlg.to_keypoint_cmbox


def get_video_name():
    return GuiData.video_path.split('.')[0].split('/')[-1]


if __name__ == '__main__':
    run()
