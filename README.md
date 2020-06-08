
# SwimFix<br>Pose Estimation Based System for Improving Front Crawl 
## Introduction
This is a official git repository for the graduation project of our B<span>.Sc. in Software Engineering in Ben Gurion University of the Negev located in Be'er Sheva, Israel.
We developed a system for improving front crawl swimming which relies on pose estimation of the swimmer.
The system takes as input a video of swimming in a front crawl setting and outputs an evaluation for the swimmer to improve upon.

## Features
- **Functionality**:
    - **2D real-time multi-person keypoint detection**:
        - 18 keypoint body keypoint estimation based on the OpenPose library.
    - **Performance evaluation** of the swimmer.
    - **Visualization** of the swimmer's keypoints and angles in each frame.
    - **Model Testing and Evaluation** including manual video annotation expected swimmer's pose vs actual swimmer's pose.
- **Input**: Video of the swimmer in a front setting (i.e. the camera is located at the end of the pool's track and faces the swimmer as he swims towards it).
- **Output**:
	- Keypoints display (PNG, JPG, MP4 and saving (CSV).
	- Graphs of the keypoints' coordinates in each frame of the video.
	- Graphs of the angles of the swimmer's shoulder/elbows/wrists in each frame of the video.
- **OS**: Ubuntu 18.04 for inference/training, Windows 10 for inference only.
- **Training**:  Train your own model on your own data.
 
 <p align="center">
    <img src="https://github.com/roeegro/SwimmingProject/blob/master/client/src/static/img/8027.gif", width="480"></p>
    
## Web Client
Our client-side consists of a Flask based web client
The client allows users to upload a video of a front crawl swimming. The video is then sent to our server and receive various insights that can hopefully improve the swimmer's performance.
For detailed information and guidelines please visit [our](https://github.com/roeegro/SwimFix/blob/master/client/README.md) guide.
## Inference Module
Our server-side consists of a inference module based on the [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose) library which estimates the swimmer's pose in every frame of the video given as input from the web client and then evaluates the swimmer's performance based on the estimation.
To install OpenPose, please check [our](https://github.com/roeegro/SwimmingProject/blob/master/server/OpenPoseSetupGuide.md) quick guide or go to the official repository linked above.
## Training Infrastructure
We created a training infrastructure for training your own custom model on your own data using the official  [OpenPose Training](https://github.com/CMU-Perceptual-Computing-Lab/openpose_train) repository.
For more information about it and a guide how to set it up and use it, please check [this](https://github.com/roeegro/SwimmingProject/blob/master/training/OpenPose%20Train%20Setup%20Guide.md) out.

> **Note:** We have also experienced with another Pose Estimation library called [OpenPose-Plus](https://github.com/tensorlayer/openpose-plus) but we do not recommend it at the moment since our inference module is using [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose) which is integrated side-by-side with the above  [OpenPose Training](https://github.com/CMU-Perceptual-Computing-Lab/openpose_train) repository.
## Results
In this section we will showcase some of our results.
## Useful Links
https://github.com/h2non/filetype.py/issues/17
https://linuxize.com/post/how-to-install-ffmpeg-on-ubuntu-18-04/
https://github.com/facebook/prophet/issues/418
https://stackoverflow.com/questions/59711301/install-pyqt5-5-14-1-on-linux
<!--stackedit_data:
eyJoaXN0b3J5IjpbNzg5MTgzODE0LDE0NjMzMjA5NywtMTUxMz
IwMDA3LDY3MzI5ODM1LC04MjEwMTk5NTAsMTI2OTM0Njk1MSwx
OTM1NDgyMzA2LDE1MDAzNDI5NzgsLTM5MDM3NDc4MywxMjM4OD
U2MTA0XX0=
-->