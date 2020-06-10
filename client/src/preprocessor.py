# Edited by Roee Groiser

import math
from imutils.video import VideoStream
import imutils
import time
import cv2
import os

from moviepy.config import get_setting
from moviepy.tools import subprocess_call

output_dir = "partial_movies/"


# if the video_path argument is 0, then we are reading from webcam
def get_video_name_from_path(video_path):
    video_path = video_path.replace('\\', '/')
    video_name = video_path.split('/')[-1]
    video_name = video_name.split('.')[0]
    return video_name


def video_cutter(video_path=0, should_take_full_video=False):
    """ Cuts the video to relevant parts for analysis.

    :param video_path: Path to video file to be trimmed. By default it will redirect to the webcam.
    :param should_take_full_video: Flag to decide whether to trim video (default), or not (while sent for testing).
    :return: List of paths to the partial videos.
    """
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

    ####### PARAMETERS ######
    MIN_AREA = 1600  # motion sensitivity factor - area wise
    PIXEL_THRESH = 40  # pixel sensitivity factor - the delta per pixel
    UNDETECTED_FRAMES_THRESH = 30  # number of undetected motion frames before stop recording
    OMIT_CLIPS_BELOW = 2  # ignore videos with length < OMIT_CLIPS_BELOW seconds
    DEBUG_MODE = 0  # visual feedback and prints
    #########################

    is_recording = False
    frame_counter = 0
    num_frames_not_detected_in_seq = 0
    prev_cnt = 0
    prev_trend = 0
    trend = 0  # to calculate if the swimmer is getting away from the camera
    trend_diff = 0
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
        if frame is not None:
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
        thresh = cv2.threshold(frame_delta, PIXEL_THRESH, 255, cv2.THRESH_BINARY)[1]

        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:1]  # Taking the biggest contour
        found_contour_in_area = False
        # loop over the contours - in this implementation there is only the biggest contour
        for c in cnts:
            # if the contour is too small, ignore it
            if DEBUG_MODE:
                print("frame number: " + str(frame_counter) + " contourArea: " + str(
                    cv2.contourArea(c)) + " trend: " + str(trend) + " trend diff: " + str(trend_diff))

            if cv2.contourArea(c) < MIN_AREA:
                trend = 0
                continue

            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # if the current figure (aka contour) is bigger than the previous one - the swimmer is getting closer
            trend = trend + 1 if (cv2.contourArea(c) - prev_cnt > 0) else trend - 1
            prev_cnt = cv2.contourArea(c)

            # every second we calculate if the figure is getting closer to the camera or getting away from it
            if not (frame_counter % int(fps)):
                trend_diff = trend - prev_trend
                prev_trend = trend
            # motion detected
            found_contour_in_area = True

            # if there is movement towards the camera and record is off - start recording
            if not is_recording and trend_diff >= 0:
                starting_timestamps.append(frame_counter * 1.0 / fps)
                starting_frames.append(frame_counter)

                is_recording = True

        if DEBUG_MODE:
            cv2.imshow("Security Feed", frame)
            cv2.imshow("Thresh", thresh)
            cv2.imshow("Frame Delta", frame_delta)
            key = cv2.waitKey(1) & 0xFF

        # update num of undetected frames in sequence if necessary
        num_frames_not_detected_in_seq = 0 if found_contour_in_area else num_frames_not_detected_in_seq + 1

        # if there are more then 30 undetected frames in seq from the last frame detected
        # or the figure is getting away from the camera- end current recording
        if (num_frames_not_detected_in_seq > UNDETECTED_FRAMES_THRESH or trend_diff < 0) and is_recording:
            ending_timestamps.append(frame_counter * 1.0 / fps)
            is_recording = False

        frame_counter += 1

    # finished looping on the video
    if is_recording:
        ending_timestamps.append(frame_counter * 1.0 / fps)
    vs.stop() if video_path == 0 else vs.release()
    cv2.destroyAllWindows()
    video_name = get_video_name_from_path(video_path)
    new_videos_paths = []
    for start_frame, start_time, end_time in zip(starting_frames, starting_timestamps, ending_timestamps):
        if DEBUG_MODE: print("Detected start time: " + str(start_time) + " Detected end time: " + str(end_time))

        if end_time - start_time < OMIT_CLIPS_BELOW:
            if DEBUG_MODE: print("Omitting the clip")
            continue

        # making sure the start and end time are integers or else
        # the extract_subclip may provide a video with black frames at the start/end of the video
        new_start_time = math.floor(start_time) - 2
        if new_start_time < 0:
            new_start_time = 0
        new_end_time = math.ceil(end_time)
        start_frame = int(new_start_time * fps)
        target_path = output_dir + video_name + '_from_frame_' + str(start_frame) + '.mp4'

        if DEBUG_MODE:
            print("Actually cutting between " + str(new_start_time) + " to " + str(new_end_time))
            print(target_path)

        extract_subclip(video_path, new_start_time, new_end_time, target_path)
        new_videos_paths.append(target_path)

    print(new_videos_paths)

    if new_videos_paths == []:
        target_path = output_dir + video_name + '_from_frame_' + str(0) + '.mp4'
        extract_subclip(video_path, 0, math.ceil(frame_counter * fps), target_path)
        new_videos_paths.append(target_path)

    # if this argument is true, send the full video without cutting it
    if should_take_full_video:
        target_path = output_dir + video_name + '_from_frame_' + str(0) + '.mp4'
        extract_subclip(video_path, 0, math.ceil(frame_counter * fps), target_path)
        return [target_path]

    return new_videos_paths


def extract_subclip(filename, t1, t2, targetname):
    """ Creates sub video file between intervals [t1,t2] in seconds named by targetname.
    :param filename: Input file path
    :param t1: Start interval time (in seconds)
    :param t2: End interval time (in seconds)
    :param targetname: Output file path.
    """
    # """ Makes a new video file playing video file ``filename`` between
    #     the times ``t1`` and ``t2``. """
    name, ext = os.path.splitext(filename)
    cmd = [get_setting("FFMPEG_BINARY"), "-y",
           "-i", filename,
           "-ss", "%.2f" % t1,
           "-to", "%.2f" % t2,
           "-vcodec", "copy", "-an", targetname]

    subprocess_call(cmd)
