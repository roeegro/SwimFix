
# OpenPose Setup Guide
## Introduction
OpenPose is an open-source Pose Estimation library which is used in our project in order to estimate the swimmer's position mid-swimming and then use that estimation to evaluate the swimmer's front crawl performance and suggest ways to improve.
## How it works
The pose estimation is performed by extracting a wire frame of the swimmer in each frame of a given video of the swimmer in a front crawl setting.
A wireframe in our context is a skeleton of the swimmer which is composed by a set of key points - each key point represents a body part (e.g elbow, shoulder, wrist, e.t.c).
For more information about the wireframe structure and the ouput of OpenPose, please check the official [output](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/output.md)  doc.

## Prerequisites 
Please go to the [original prerequisites](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/prerequisites.md) doc and make sure you have all the required prerequisites on your machine based on your hardware.

## Installation
The installation is well written and explained in the official git repository, so in this section we will gather the important links for you to perform a quick and clean installation:

Please clone the git repository into `SwimmingProject/server` directory:
```
cd SwimmingProject/server
git clone https://github.com/CMU-Perceptual-Computing-Lab/openpose
cd openpose
mkdir build
cd build
cmake ..
```
Those command are based on [this](
https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/installation.md) installation doc. In case you're having trouble or want to perfom the installation differently, please check it out.

## Quick Start
Please check out [this](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/quick_start.md) quick start doc to get familiar with OpenPose and check that everything works fine.

## Training
For training OpenPose on custom data and creating your own model, please check out [our](https://github.com/roeegro/SwimmingProject/blob/master/training/OpenPose%20Train%20Setup%20Guide.md) compelete guide.
<!--stackedit_data:
eyJoaXN0b3J5IjpbMTgwMzk0NTUwMywtMTA2NjA0NzEzNSwtNj
E2NDMzMzQyXX0=
-->