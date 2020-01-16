# Edited by Roee Groiser

# import the necessary packages
from imutils.video import VideoStream
import imutils
import time
import cv2
from moviepy.editor import *
import os
from natsort import natsorted


# if the video_path argument is 0, then we are reading from webcam

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
    # loop over the frames of the video
    while True:
        # grab the current frame and initialize the occupied/unoccupied
        # text
        frame = vs.read()
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
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < min_area:
                continue

            # (x, y, w, h) = cv2.boundingRect(c)
            # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # motion detected
            found_countour_in_area = True

            if is_recording:  # if recording just write the frame to the partial_output
                partial_output.write(frame)
                # cv2.imshow('frame', frame)
            else:  # otherwise - open new partial movie and write the first detected frame.
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                fps=vs.get(5)
                partial_output = cv2.VideoWriter(
                    '../../server/partial_movies/partial_output_from_frame_{}.mp4'.format(frame_counter), fourcc, vs.get(5),
                    (frame.shape[1], frame.shape[0]))
                partial_output.write(frame)
                # cv2.imshow('frame', frame)
                is_recording = True

        # update num of undetected frames in sequence if necessary
        num_frames_not_detected_in_seq = 0 if found_countour_in_area else num_frames_not_detected_in_seq + 1
        found_countour_in_area = False

        # if there are more then 4 undetected frames in seq from the last frame detected - save the partial movies
        if num_frames_not_detected_in_seq > 30 and not partial_output is None:
            partial_output.release()
            partial_output = None
            is_recording = False
            num_frames_not_detected_in_seq = 0
        # cv2.imshow("Video processor", frame)  # TODO: Remove this command when you finish
        # delay of 25 ms between frames
        key = cv2.waitKey(25) & 0xFF
        # exit can be done by pressing 'q'
        if key == ord("q"):
            break
        frame_counter += 1

    # Close all resources
    if is_recording and not partial_output is None:
        partial_output.release()
    vs.stop() if video_path == 0 else vs.release()
    cv2.destroyAllWindows()

    lst = []

    for root, dirs, files in os.walk('../../server/partial_movies/'):
        files = natsorted(files)
        print(files)
        for file in files:
            if os.path.splitext(file)[1] == '.mp4':
                file_path = os.path.join(root, file)
                print(file_path)
                video = VideoFileClip(file_path)
                print(video)
                lst.append(video)

    print(lst)
    final_clip = concatenate_videoclips(lst)
    final_clip.to_videofile("../../server/partial_movies/output.mp4", fps=fps, remove_temp=False)
