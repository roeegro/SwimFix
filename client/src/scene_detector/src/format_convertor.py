from converter import Converter
import subprocess


def convert_video(video_input, video_output):
    cmds = ['ffmpeg', '-i', video_input, video_output]
    process = subprocess.run(cmds)


if __name__ == "__main__":
    # convert()
    convert_video('../Videos/MVI_8012.MOV', '../Videos/8012.mp4')