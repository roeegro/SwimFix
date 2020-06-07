# OpenPose and Setup Guide
## Table of Contents
1. [What is OpenPose?](#what-is-openpose)
2. [How It Works?](#how-it-works)
3. [Prerequisites](#prerequisites)
4. [Quick Start](#quick-start)
5. [Training](#training)

## What is OpenPose?
OpenPose is an open-source Pose Estimation library which is used in our project in order to estimate the swimmer's position mid-swimming and then use that estimation to evaluate the swimmer's front crawl performance and suggest ways to improve.

![Estimating partial human poses – mc.ai](https://cdn-images-1.medium.com/max/1000/0*vLPWgysrOYR7aP5C.gif)

## How It Works?
The pose estimation is performed by extracting a wire frame of the swimmer from each frame of a given video of the swimmer in a front crawl setting.
A wire frame is a skeleton of the swimmer which is composed by a set of key points - each key point represents a body part (e.g elbow, shoulder, wrist, e.t.c).
For more information about the wire frame structure and the output of OpenPose, please check the official [output](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/output.md)  doc.<br>
![](https://github.com/CMU-Perceptual-Computing-Lab/openpose/raw/master/doc/media/keypoints_pose_18.png)
<p align="center">
    <img src="https://github.com/CMU-Perceptual-Computing-Lab/openpose/raw/master/doc/media/keypoints_pose_18.png", width="480"></p>

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
eyJoaXN0b3J5IjpbNDE2MjA2Niw1OTExMTgyNTNdfQ==
-->