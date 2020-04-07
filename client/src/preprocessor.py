# Edited by Roee Groiser

# import the necessary packages
# import math

from imutils.video import VideoStream
import imutils
import time
import timeit
import cv2
import os

from moviepy.config import get_setting
from moviepy.tools import subprocess_call

output_dir = "partial_movies/"


# if the video_path argument is 0, then we are reading from webcam
def get_video_name_from_path(video_path):
    video_name = video_path.split('/')[-1]
    video_name = video_name.split('\\')[-1]
    video_name = video_name.split('.')[0]
    return video_name


def video_cutter(video_path=0):
    if video_path == 0:
        vs = VideoStream(src=0).start()
        time.sleep(2.0)
    # otherwise, we are reading from a video file
    else:
        vs = cv2.VideoCapture(video_path)
    partial_output = None

    # initialize the first frame in the video stream
    first_frame = vs.read()[1]
    first_frame = imutils.resize(first_frame, width=500)
    first_frame = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
    first_frame = cv2.GaussianBlur(first_frame, (21, 21), 0)
    min_area = 4000  # motion sensitivity factor
    # initialize counter
    # saving this variables in order to avoid duplicate checking of the same elapsed time
    is_recording = False
    frame_counter = 0
    num_frames_not_detected_in_seq = 0
    starting_frames = []
    starting_timestamps = []
    ending_timestamps = []
    # loop over the frames of the video
    while True:
        # grab the current frame and initialize the occupied/unoccupied
        # text
        frame = vs.read()
        fps = vs.get(5)
        frame = frame if video_path == 0 else frame[1]
        if not frame is None:
            frame_shape = frame.shape

        # if the frame could not be grabbed, then we have reached the end
        # of the video
        if frame is None:
            break

        # resize the frame, convert it to grayscale, and blur it
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (13, 13), 0)
        # cv2.imshow('gray', gray)

        # if the first frame is None, initialize it
        if first_frame is None:
            first_frame = gray
            continue

        # compute the absolute difference between the current frame and
        # first frame
        frame_delta = cv2.absdiff(first_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        found_countour_in_area = False
        # loop over the contours
        # contour_area_lst = []
        # i = 0
        for c in cnts:
            # if the contour is too small, ignore it
            # i += 1
            # contour_area_lst.append(cv2.contourArea(c))
            # print(str(i)+" - " + str(cv2.contourArea(c)))

            print(cv2.contourArea(c))
            if cv2.contourArea(c) < min_area:
                continue

            # if cv2.contourArea(c) < max(contour_area_lst[-6:-1]):
            #     print("contour lowers")
            #     continue

            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # motion detected
            found_countour_in_area = True

            if not is_recording:  # otherwise - open new partial movie and write the first detected frame.
                starting_timestamps.append(frame_counter * 1.0 / fps)
                starting_frames.append(frame_counter)

                is_recording = True

        cv2.imshow("Security Feed", frame)
        cv2.imshow("Thresh", thresh)
        cv2.imshow("Frame Delta", frame_delta)
        key = cv2.waitKey(1) & 0xFF

        # update num of undetected frames in sequence if necessary
        num_frames_not_detected_in_seq = 0 if found_countour_in_area else num_frames_not_detected_in_seq + 1
        found_countour_in_area = False
        # show the frame and record if the user presses a key

        # if there are more then 30 undetected frames in seq from the last frame detected - save the partial movies
        if num_frames_not_detected_in_seq > 100 and is_recording:
            ending_timestamps.append(frame_counter * 1.0 / fps)
            is_recording = False
            num_frames_not_detected_in_seq = 0

        frame_counter += 1

    if is_recording:
        ending_timestamps.append(frame_counter * 1.0 / fps)
    vs.stop() if video_path == 0 else vs.release()
    cv2.destroyAllWindows()
    video_name = get_video_name_from_path(video_path)
    new_videos_paths = []
    for start_frame, start_time, end_time in zip(starting_frames, starting_timestamps, ending_timestamps):
        print("start time: " + str(start_time) + " end time: " + str(end_time))
        target_path = output_dir + video_name + '_from_frame_' + str(start_frame) + '.mp4'
        print(target_path)
        extract_subclip(video_path, start_time, end_time, target_path)
        new_videos_paths.append(target_path)

    print(new_videos_paths)
    return new_videos_paths


def extract_subclip(filename, t1, t2, targetname):
    """ Makes a new video file playing video file ``filename`` between
        the times ``t1`` and ``t2``. """
    name, ext = os.path.splitext(filename)

    cmd = [get_setting("FFMPEG_BINARY"), "-y",
           "-i", filename,
           "-ss", "%0.2f" % t1,
           "-t", "%0.2f" % (t2 - t1),
           "-vcodec", "copy", "-an", targetname]

    subprocess_call(cmd)
