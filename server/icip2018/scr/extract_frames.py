import cv2
import os


def extract_frames_by_folder(parent):
    for swimmer in next(os.walk(parent + '\.'))[1]:
        extract_frames_by_file(parent + swimmer + "\\" + swimmer + ".MOV", parent + swimmer)


def extract_frames_by_file(file, output):
    vidcap = cv2.VideoCapture(file);
    if not os.path.exists(output + "\\frames"):
        os.makedirs(output + "\\frames")
    if not os.path.exists(output + "\\poses"):
        os.makedirs(output + "\\poses")
    if not os.path.exists(output + "\\images"):
        os.makedirs(output + "\\images")

    success, image = vidcap.read()
    count = 0
    while success:
        success, image = vidcap.read()
        print('Read a new frame: ', count, success)
        cv2.imwrite(output + "\\frames\\frame_%d.jpg" % count, image)  # save frame as JPEG file
        count += 1

        # if __name__ == "__main__":
        # extract_frames_by_folder(parent="D:\ComputerVision\\test_data\\")
        # extract_frames_by_file(file="D:\ComputerVision\\test_data\Bobby\Bobby.MOV", output="D:\ComputerVision\\test_data\Bobby\\")
