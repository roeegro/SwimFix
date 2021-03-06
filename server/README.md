# OpenPose and Setup Guide
## Table of Contents
1. [What is OpenPose?](#what-is-openpose)
2. [How It Works?](#how-it-works)
3. [Prerequisites](#prerequisites)
4. [Quick Start](#quick-start)
5. [Training](#training)

## What is OpenPose?
OpenPose is an open-source Pose Estimation library which is used in our project in order to estimate the swimmer's position mid-swimming and then use that estimation to evaluate the swimmer's front crawl performance and suggest ways to improve.

 <p align="center">
    <img src="https://github.com/roeegro/SwimmingProject/blob/master/client/src/static/img/8027.gif", width="480"></p>

## How It Works?
The pose estimation is performed by a keypoint detection of the object (in our case, the swimmer) and extracting a wire frame of it from each frame of the given video (in our case, a video of the swimmer in a front crawl setting).

A wire frame is the output of Opsepose - it is a skeleton of the swimmer which is composed by a set of key points - each key point represents a body part (e.g elbow, shoulder, wrist, e.t.c). 

<p align="center">
    <img src="https://github.com/CMU-Perceptual-Computing-Lab/openpose/raw/master/doc/media/keypoints_pose_18.png", width="480"></p>

For more information about the wire frame structure and the output of OpenPose, please check the official [output](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/output.md)  doc.<br>

## Installation

> **Prerequisites**
> Please go to the [official](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/prerequisites.md) prerequisites doc and make sure you have all the required prerequisites on your machine based on your hardware.



Clone the git repository into `SwimmingProject/server` directory and run:
```
cd SwimmingProject/server
git clone https://github.com/CMU-Perceptual-Computing-Lab/openpose
cd openpose
mkdir build
cd build
cmake ..
```
These commands are based on the [official](
https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/installation.md#cmake-command-line-configuration-ubuntu-only) installation doc. In case you're having trouble or want to perfom the installation differently, please check it out.

## Quick Start
Please check out [this](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/quick_start.md) quick start doc to get familiar with OpenPose and check that everything works fine.

## Training
For training OpenPose on custom data and creating your own model, please check out [our](https://github.com/roeegro/SwimmingProject/blob/master/training/OpenPose%20Train%20Setup%20Guide.md) complete guide, which is based on the [official](https://github.com/CMU-Perceptual-Computing-Lab/openpose_train) OpenPose Training repository and contains all the information you need in order to train a model from scratch.

<!--stackedit_data:
eyJoaXN0b3J5IjpbOTI2Nzc4MjIyLDEyNDg5NTUzMDgsMTgzOT
gxOTQ0OSwtMTM4MjAyOTY5Niw1OTExMTgyNTNdfQ==
-->