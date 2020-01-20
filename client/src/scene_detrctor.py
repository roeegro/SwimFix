import os
import format_convertor
import scenedetect
from scenedetect.video_manager import VideoManager
from scenedetect.scene_manager import SceneManager
from scenedetect.frame_timecode import FrameTimecode
from scenedetect.stats_manager import StatsManager
from scenedetect.detectors import ContentDetector
from scenedetect.video_splitter import *
import argparse

stats_file_path = '../testvideo.stats.csv'


def preprocess(vid_name):
    # Create a video_manager point to video file testvideo.mp4. Note that multiple
    # videos can be appended by simply specifying more file paths in the list
    # passed to the VideoManager constructor. Note that appending multiple videos
    # requires that they all have the same frame size, and optionally, framerate.

    # Assign path to original video and mp4 video and convert if needed
    vid_path = '../Videos/MVI_' + vid_name + '.MOV'
    mp4_vid_path = '../Videos/' + vid_name + '.mp4'
    if not os.path.exists(mp4_vid_path):
        format_convertor.convert_video(vid_path, mp4_vid_path)

    # Assign paths to the main video result dir and State csv file
    vid_result_dir_path = '../Results/' + vid_name
    stats_file_path = vid_result_dir_path + '/' + vid_name + '.stats.csv'

    video_manager = VideoManager([mp4_vid_path])
    stats_manager = StatsManager()
    scene_manager = SceneManager(stats_manager)
    # Add ContentDetector algorithm (constructor takes detector options like threshold).
    scene_manager.add_detector(ContentDetector())
    base_timecode = video_manager.get_base_timecode()

    try:
        # If stats file exists, load it.
        if not os.path.exists(vid_result_dir_path):
            os.mkdir(vid_result_dir_path)
            # stats_file_path += '/' + vid_name + '.stats.csv'
        # Read stats from CSV file opened in read mode:
        if os.path.exists(stats_file_path):
            # stats_file_path += '/' + vid_name + '.stats.csv'
            with open(stats_file_path, 'r') as stats_file:
                stats_manager.load_from_csv(stats_file, base_timecode)

        # start_time = base_timecode + 20  # 00:00:00.667
        # end_time = base_timecode + 20.0  # 00:00:20.000
        # # Set video_manager duration to read frames from 00:00:00 to 00:00:20.
        # video_manager.set_duration(start_time=start_time, end_time=end_time)

        # Set downscale factor to improve processing speed (no args means default).
        video_manager.set_downscale_factor()

        # Assign the path to the Scenes csv file
        scenes_file_path = '../Results/' + vid_name + '/' + vid_name + '.scenes.csv'

        # Start video_manager.
        video_manager.start()

        # Perform scene detection on video_manager.
        scene_manager.detect_scenes(frame_source=video_manager)

        # Obtain list of detected scenes.
        scene_list = scene_manager.get_scene_list(base_timecode)
        # Like FrameTimecodes, each scene in the scene_list can be sorted if the
        # list of scenes becomes unsorted.
        with open(scenes_file_path, 'w+') as scenes_file:
            scenedetect.scene_manager.write_scene_list(scenes_file, scene_list)

        print('List of scenes obtained:')
        for i, scene in enumerate(scene_list):
            print('    Scene %2d: Start %s / Frame %d, End %s / Frame %d' % (
                i + 1,
                scene[0].get_timecode(), scene[0].get_frames(),
                scene[1].get_timecode(), scene[1].get_frames(),))

        # We only write to the stats file if a save is required:
        if stats_manager.is_save_required():
            with open(stats_file_path, 'w+') as stats_file:
                stats_manager.save_to_csv(stats_file, base_timecode)

        # Split the video based on the given detectors
        template = '$VIDEO_NAME-Scene-$SCENE_NUMBER.mp4'
        split_video_ffmpeg(video_manager.get_video_paths(), scene_list, output_file_template=template,
                           video_name='../Results/' + vid_name + '/' + vid_name, suppress_output=True)
    finally:
        video_manager.release()


if __name__ == "__main__":
    preprocess('8162')
