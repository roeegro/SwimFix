# Edited by Roee Groiser

# import the necessary packages
# import math

from imutils.video import VideoStream
import imutils
import time
import timeit
import cv2
from moviepy.editor import *
import os

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.config import get_setting
from moviepy.tools import subprocess_call
from natsort import natsorted
from moviepy.video.io.VideoFileClip import VideoFileClip

# from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
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
            if cv2.contourArea(c) < min_area:
                continue

            # if cv2.contourArea(c) < max(contour_area_lst[-6:-1]):
            #     print("contour lowers")
            #     continue

            # (x, y, w, h) = cv2.boundingRect(c)
            # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # motion detected
            found_countour_in_area = True

            if not is_recording:  # otherwise - open new partial movie and write the first detected frame.
                starting_timestamps.append(frame_counter * 1.0 / fps)
                starting_frames.append(frame_counter)
                # fourcc = cv2.VideoWriter_fourcc(*'mp4v')

                # partial_output = cv2.VideoWriter(
                #     'partial_movies/partial_output_from_frame_{}.mp4'.format(frame_counter), fourcc, vs.get(5),
                #     (frame.shape[1], frame.shape[0]))
                # partial_output.write(frame)

                # cv2.imshow('frame', frame)
                is_recording = True

        # update num of undetected frames in sequence if necessary
        num_frames_not_detected_in_seq = 0 if found_countour_in_area else num_frames_not_detected_in_seq + 1
        found_countour_in_area = False

        # if there are more then 30 undetected frames in seq from the last frame detected - save the partial movies
        if num_frames_not_detected_in_seq > 30 and not partial_output is None:
            partial_output.release()
            ending_timestamps.append(frame_counter * 1.0 / fps)
            partial_output = None
            is_recording = False
            num_frames_not_detected_in_seq = 0

        frame_counter += 1

    # Close all resources
    if is_recording and not partial_output is None:
        partial_output.release()

    ending_timestamps.append(frame_counter * 1.0 / fps)
    vs.stop() if video_path == 0 else vs.release()
    cv2.destroyAllWindows()
    video_name = get_video_name_from_path(video_path)
    new_videos_paths = []
    for start_frame, start_time, end_time in zip(starting_frames, starting_timestamps, ending_timestamps):
        print(video_path)
        timer_start = time.time()
        target_path = output_dir + video_name + '_from_frame_' + str(start_frame) + '.mp4'
        print(target_path)
        extract_subclip(video_path, start_time, end_time, target_path)
        timer_end = time.time()
        print("Ended extracting a clip in total of " + str(timer_end - timer_start) + " seconds")
        new_videos_paths.append(target_path)
        # video = VideoFileClip(video_path)
        # new = video.subclip(start_time, end_time)
        # new.write_videofile(output_dir + 'partial_output_from_frame_{}.mp4'.format(start_frame), audio=False)

    # concatenate videos - currenty we dont want to use it
    # lst = []
    # file_path = 0
    # for root, dirs, files in os.walk(output_dir):
    #     files = natsorted(files)
    #     # print(files)
    #     for file in files:
    #         if os.path.splitext(file)[1] == '.mp4':
    #             file_path = os.path.join(root, file)
    #             # print(file_path)
    #             lst.append(VideoFileClip(file_path))
    #
    # original_video_name = video_path.split('\\')[-1]
    # print(video_path)
    # print(original_video_name)
    # if len(lst) > 1:
    #     final_clip = concatenate_videoclips(lst)
    #     final_clip.to_videofile(output_dir + original_video_name, fps=fps, remove_temp=True)
    #     final_clip.close()
    #     for video in lst:
    #         video.close()
    # elif len(lst):
    #     lst[0].close()
    #     os.rename(file_path, output_dir + original_video_name)

    # return original_video_name
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
