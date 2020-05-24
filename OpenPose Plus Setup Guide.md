# OpenPose-Plus Setup Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Custom Model Training](#custom-model-training)
   * [Training Configuration](#training-configuration)
   * [Additional steps for training on Windows](#additional-steps-for-training-on-windows)
5. [Our Training Recap](#our-training-recap)
   * [Our Configuration](#configuration)
   * [Our Data](#our-data)
   *  [Our Results](#our-results)
## Introduction
This is a complete guide for setting up the [OpenPose-Plus](https://github.com/tensorlayer/openpose-plus) which is another pose-estimataion library we experienced with in our [Swimming Project](https://github.com/roeegro/SwimmingProject).
For our project, we used a forked version of the original library which you can find [here](https://github.com/bela127/openpose-plus).
After forking, we made some changes to a couple of files and made our own version which you will work with and can be found [here](https://github.com/tommarz/openpose_train).
Throughout this guide we will walk through all the required steps for training a custom model on your own data, top to bottom.
From now on the `openpose-plus` directory will be our working directory and the `SwimmingProject` directory which is the main directory of our git repository will be our root directory.
> **Note**: This guide is related on training a model on a COCO formatted custom data **only**. 
>  In case you want to train a model just on the COCO dataset rather than your own, please follow the original repository instructions. You can read more about the COCO dataset which the OpenPose default COCO model was trained on [here](http://cocodataset.org/).
### Disclaimer
This guide is based on a setup we successfully managed to perform on an AWS EC2 virtual machine with the following AMI:<br>**AWS Deep Learning AMI (Ubuntu 18.04)** (more details  [here](https://aws.amazon.com/marketplace/pp/B07Y43P7X5?ref=cns_srchrow))
Keep in mind that this machine is delivered with all the NVIDIA related prerequesities that are mandatory for both OpenPose training and inference versions (The full list of prerequesities for the inference version is [here](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/prerequisites.md))
This means the guide assumes you are running on a a similiar machine.
## Prerequisites
Training the model is implemented using TensorFlow. To run `train.py`, you would need to install packages, shown
in [requirements.txt](https://github.com/tensorlayer/openpose-plus/blob/master/requirements.txt), in your virtual environment (**Python 3**):
```bash
pip3 install -r requirements.txt
pip3 install pycocotools
```
## Custom Model Training

`train.py` automatically download MSCOCO 2017 dataset into `data/mscoco17`.
The default model is VGG19 used in the OpenPose paper.
To customize the model, simply changing it in `models.py`.

### Custom Data
In case you wish to train a model on your own data you need to create an annotation file in JSON format for that data. Make sure to annotate in the [COCO Format](http://cocodataset.org/#format-data).

For annotating our data we used the [coco-annotator](https://github.com/jsbroks/coco-annotator) repository which is cloned in the root directory under the name `coco-annotator`. We recommend you to use it as well. Please check out [this](https://docs.google.com/document/d/1CnZHzUDVSLxYTczuYnHGJrh37uqOqPRSNcRDbleLI5w/edit?usp=sharing) guide we wrote regarding installation and correct usage.

1. Use the above annotator (or any other annotator) in order to annotate your data in the correct format.
2.  Export the annotated data to a JSON file in a  to `data/your_data/` folder and name it `coco.json` .
3. Copy the [dataset folder](#step-0---data-import) from step 0 to `dataset/COCO/cocoapi/images/` folder.

At the end of this step you should have:
- An annotations JSON file located in `dataset/COCO/cocoapi/annotations/person_keypoints_custom.json`
- A [dataset folder](#step-0---data-import) with the raw images located in `dataset/COCO/cocoapi/images/custom`
### Training Configuration
You can use `train_config.py` to configure the training. `config.DATA.train_data` can be:
* `coco`: training data is COCO dataset only (original default)
* `custom`: training data is your dataset specified by `config.DATA.your_xxx`(our default)
* `coco_and_custom`: training data is COCO and your dataset

`config.MODEL.name` can be:
* `vgg`: VGG19 version (original default), slow
* `vggtiny`: VGG tiny version, faster
* `mobilenet`: MobileNet version, faster
* `hao28_experimental`: A model we added (our default)
### Training
Train your model by running:
```bash
python3 train.py
```
### Additional steps for training on Windows
There are a few extra steps to follow with Windows. Please make sure you have the following prerequisites installed:
* [git](https://git-scm.com/downloads)
* [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
* [wget](https://eternallybored.org/misc/wget/)

Download the wget executable and copy it into one of your folders in System path to use the wget command from anywhere. Use the `path` command in command line to find the folders. Paste the wget.exe in one of the folders given by `path`. An example folder is `C:\Windows`.

pycocotools is not supported by default on Windows. Use the pycocotools build for Windows at [here](https://github.com/philferriere/cocoapi). Instead of `pip install pycocotools`, using:
```bash
pip install git+https://github.com/philferriere/cocoapi.git#subdirectory=PythonAPI
```
Visual C++ Build Tools are required by the build. Everything else is the same.

## Our Training Recap
In this section we will share our experience with training a custom model for our project.
### Our Configuration
For our training, some changes were made in the `train_config.py` file:
- The `hao28_experimental` model is used instead of the default `VGG19` -- The initial weights are changed from random to pre-trained weights `hao28-pose600000.npz` which were originally trained on `mscoco2017` dataset that we mentioned earlier.
- The learning rate is lowered from `4e-5` to `1.641157e-07`
- The weight decay step decreased from `136106` to `100000`
### Our Data
We trained our model on a custom data which consists of about 1100 images in 640x480 resolution of swimming pools with one person swimming - **the are no images with empty pool at all.**
### Our Results
We managed to achieve model loss of about 2.11 in 67726 iterations and saved the learned weights  as `pose_best_67726_2.118974208831787_.npz` in the `models` directory.

## High-performance Inference using TensorRT

Real-time inference on resource-constrained embedded platforms is always challenging. To resolve this, we provide a TensorRT-compatible inference engine.
The engine has two C++ APIs, both defined in `include/openpose-plus.hpp`.
They are for running the TensorFlow model with TensorRT and post-processing respectively.

For details of inference(dependencies/quick start), please refer to [**cpp-inference**](doc/markdown-doc/cpp-inference.md).

We are improving the performance of the engine.
Initial benchmark results for running the full OpenPose model are as follows.
On Jetson TX2, the inference speed is 13 frames / second (the mobilenet variant is even faster).
On Jetson TX1, the speed is 10 frames / second. On Titan 1050, the speed is 38 frames / second. 

After our first optimization, we achieved 50FPS(float32) on 1070Ti. 

We also have a Python binding for the engine. The current binding relies on
the external tf-pose-estimation project. We are working on providing the Python binding for our high-performance
C++ implementation. For now, to enable the binding, please build C++ library for post processing by:

```bash
./scripts/install-pafprocess.sh
# swig is required. Run `conda install -c anaconda swig` to install swig.
```

See [tf-pose](https://github.com/ildoonet/tf-pose-estimation/tree/master/tf_pose/pafprocess) for details.
<!--stackedit_data:
eyJoaXN0b3J5IjpbMTEwNzYwMTg1MSwtMzg3MDY2NjI5LDU0OT
A1NTIwOCwxMjA1MjA2NTc2XX0=
-->