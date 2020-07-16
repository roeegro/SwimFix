# SwimFix<br>Pose Estimation Based System for Improving Front Crawl 

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Web Client](#web-client)
4. [Inference Server](#inference-server)
5. [Training Infrastructure](#training-infrastructure)

## Introduction
This is an official git repository for the graduation project of our B<span>.Sc. in Software Engineering in Ben Gurion University of the Negev located in Be'er Sheva, Israel.
We have developed a system for improving front crawl swimming which relies on pose estimation of the swimmer.
The system takes as input a video of swimming in a front crawl setting and outputs a feedback for the swimmer to improve upon.<br>
Wix site: https://tommarz.wixsite.com/graduation-project/

## Features
- **Functionality**:
    - **2D real-time multi-person keypoint detection**:
        - 18 body keypoints estimation using the [OpenPose](#https://github.com/CMU-Perceptual-Computing-Lab/openpose)™ library.
    - **Performance Assessment** of the swimmer:
	    - Error detection including multiple error types.
	    - Manual error fixing over the frames where the error occurred
	    - Final assessment grade calculation based on the detected errors
	    - Add new types of errors on the fly [Plug and Play]
    - **Extraction & Visualization** of various performance measures:
		- The keypoints' coordinates.
		- The angles of the swimmer's shoulders/elbows/wrists.
		- Graph for every measure with its value in every frame of the video
    - **Model Testing and Evaluation**
	    - Manual video annotation tool to set the expected result.
	    - Expected vs actual result comparison made easy with graphs.
- **Input**: Video of the swimmer in a front setting (i.e. the camera is located at the end of the swimming pool's lane and faces the swimmer as he swims towards it).
- **Output**:
	- Keypoints display on each frame (JPG)
	- Input video with OpenPose wireframes on it (MP4)
	- Graphs of the keypoints' coordinates in each frame of the video.
	- Graphs of the angles of the swimmer's shoulder/elbows/wrists in each frame of the video.
	- List of detected swimming errors including error type and on which frame it occurred.
	- Final score based on the detected error.
- **OS**: Ubuntu 18.04, Windows 10 for web client only.
- **Training**:  Train your own model on your own data.
	- Prepare and transform your data so it can fit the model.
	- Currently we do not support deployment of the model.
	- You can find a complete walk-through guide [here](https://github.com/roeegro/SwimFix/blob/master/training/README.md).
 
>**TODO**: put the impression video here
    
## Web Client
Our client-side consists of a Flask based web client
The client allows users to upload a video of a front crawl swimming. The video is then sent to our server and receive various insights that can improve the swimmer's performance.
For detailed information and guidelines please visit [our](https://github.com/roeegro/SwimFix/blob/master/client/README.md) guide.
## Inference Server
Our server-side consists of a inference module based on the [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose) library which estimates the pose in every frame of the video given as input from the web client and then evaluates the swimmer's performance based on the estimation.
To install OpenPose, please check [our](https://github.com/roeegro/SwimFix/blob/master/server/README.md) quick guide or go to the official repository linked above.
## Training Infrastructure
We created a training infrastructure for training your own custom model on your own data using the official  [OpenPose Train](https://github.com/CMU-Perceptual-Computing-Lab/openpose_train) repository.
For more information about it and a guide how to set it up and use it, please check [this](https://github.com/roeegro/SwimFix/blob/master/training/README.md) out.

<!--stackedit_data:
eyJoaXN0b3J5IjpbMTcxODk4NzIzNV19
-->
<!--stackedit_data:
eyJoaXN0b3J5IjpbMTIxMjU2MTM0MV19
-->
