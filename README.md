
# SwimFix<br>Pose Estimation Based System for Improving Front Crawl 
## Introduction
This is a official git repository for the graduation project of our B.S.C<span>.Sc. in Software Engineering in Ben Gurion University of the Negev located in Be'er Sheva, Israel.
We developed a system for improving front crawl swimming which relies on pose estimation of the swimmer.
The system takes as input a video of swimming in a front crawl setting and outputs an evaluation for the swimmer to improve upon.

## Features
- **Functionality**:
    - **2D real-time multi-person keypoint detection**:
        - 18 keypoint body keypoint estimation based on the OpenPose library.
    - **Performance evaluation of the swimmer**
    - **Visualization of the swimmer's keypoints and angles in each frame**
- **Input**: Video of the swimmer in a front setting (i.e. the camera is located at the end of the pool and faces the swimmer)
- **Output**:
	- Basic image + keypoint display/saving (PNG, JPG, AVI, ...), keypoint saving 			(JSON, XML, YML, ...), and/or keypoints as array class.
	- Graphs for the keypoints' coordinates in each frame of the video.
	- Graphs for the angles of the swimmer's shoulder/elbows/wrists in each frame of the video
- **OS**: Ubuntu 18.04 for training, Windows 10 for inference
- **Training and datasets**:
    - [**OpenPose Training**](https://github.com/CMU-Perceptual-Computing-Lab/openpose_train).
    
## Web Client
Our client-side consists ofis a Flask based web client
## Inference System.
The client allows users to upload a video of a front crawl swimming. The video is then sent to our server and receive various insights that can hopefully improve the swimmer's performance.
For detailed information and guidelines please visit **this** page.
## Inference Module
Our server-side consists of a inference module based on the [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose) library which .
To install OpenPose, please check [our](https://github.com/roeegro/SwimmingProject/blob/master/server/OpenPoseSetupGuide.md) quick guide or go to the official repository linked above.
## Training Infrastructure
We created a training infrastructure for training your own custom model on your own data using the official  [OpenPose Training](https://github.com/CMU-Perceptual-Computing-Lab/openpose_train) repository.
For more information about it and a guide how to set it up and use it, please check [this](https://github.com/roeegro/SwimmingProject/blob/master/training/OpenPose%20Train%20Setup%20Guide.md) out.

> **Note:** We have also experienced with another Pose Estimation library called [OpenPose-Plus](https://github.com/tensorlayer/openpose-plus) but as for now we do not recommend it since our inference module is built upon [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose) which is used side-by-side with the above  [OpenPose Training](https://github.com/CMU-Perceptual-Computing-Lab/openpose_train) repository.
## Results
In this section we will showcase some of our results
## Useful Links
https://github.com/h2non/filetype.py/issues/17
https://linuxize.com/post/how-to-install-ffmpeg-on-ubuntu-18-04/
https://github.com/facebook/prophet/issues/418
https://stackoverflow.com/questions/59711301/install-pyqt5-5-14-1-on-linux
<!--stackedit_data:
eyJoaXN0b3J5IjpbMTUwMDM0Mjk3OCwtMzkwMzc0NzgzLDEyMz
g4NTYxMDRdfQ==
-->