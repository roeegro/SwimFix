# <center>OpenPose Train Setup Guide</center>

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Required Third-Party Repositories](#required-third-party-repositories)
4. [Data Preperation and Preprocessing](#data-preperation-and-preprocessing)
   * [Data Annotation](#step-1---data-annotation)
   * [Data Filtering and Reindexing](#step-2---data-filtering-and-re-indexing)
   * [Data Augmentation](#step-3---data-augmentation)
   * [LMDB File Generation](#step-4---lmdb-file-generation)
5. [Training](#training)
6. [Validation](#validation)
7. [Testing](#testing)
8. [Our Results](#our-results)
9. [Q&A](#qa)
10. [Installation Commands](#installation-commands)
## Introduction
This is a complete guide for setting up the [OpenPose Train]((https://github.com/CMU-Perceptual-Computing-Lab/openpose_train))  which is used alongside the [original](https://github.com/CMU-Perceptual-Computing-Lab/openpose) OpenPose library in our [Swimming Project](https://github.com/roeegro/SwimmingProject).
For our project, we modified some of the files in the original repository so we created a [fork](https://github.com/tommarz/openpose_train) with the updated files which you will work with.
Throughout this guide we will walk through all the required steps for training a custom model on your own data, top to bottom.
From now on the `openpose_train` directory will be our working directory and the `SwimmingProject` directory which is the main directory of our git repository will be our root directory.
> **Note**: This guide is related on training a model on a COCO formatted custom data **only**. 
>  In case you want to train a model just on the COCO dataset rather than your own, please follow the original repository instructions. You can read more about the COCO dataset which the OpenPose default COCO model was trained on [here](http://cocodataset.org/).
## Disclaimer
This guide is based on a setup we successfully managed to perform on an AWS EC2 virtual machine with the following AMI:<br>**Deep Learning Base AMI (Ubuntu 18.04) Version 22.0 (ami-0f6127e61a87f8677)** (more details  [here](https://aws.amazon.com/marketplace/pp/B07Y3VDBNS?qid=1589717278223&sr=0-1&ref_=srh_res_product_title))<br>Keep in mind that this machine is delivered with all the NVIDIA related prerequisites that are mandatory for both OpenPose training and inference versions (The full list of prerequisites for the inference version is [here](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/prerequisites.md))<br>**The guide assumes you are running on a similar machine.**

> The guide was tested successfully on an Ubuntu 18.04 machine with the following hardware:
>- Nvidia GeForce RTX 2060 GAMING Z 6G
>- Intel(R) Core(TM) i9-9900K CPU @ 3.60GHz
>- 32GB*2 DDR4 RAM

## Prerequisites
Make sure you have those and before continuing:
- Nvidia GPU related prerequisites:
    1. **Note: OpenPose has been tested extensively with CUDA 8.0 (cuDNN 5.1) and CUDA 10.0 (cuDNN 7.5)**. We highly recommend using those versions to minimize potential installation issues. Other versions should also work, but we do not provide support about any CUDA/cuDNN installation/compilation issue, as well as problems relate dto their integration into OpenPose.
    2. **CUDA**:
        - Ubuntu 14 or 16 ([**CUDA 8**](https://developer.nvidia.com/cuda-80-ga2-download-archive) **or 10**): Run `sudo ./scripts/ubuntu/install_cuda.sh` (if Ubuntu 16 or 14 and for Graphic cards up to 10XX) or alternatively download and install it from their website.
        - Ubuntu 18 ([**CUDA 10**](https://developer.nvidia.com/cuda-downloads)): Download the latest Nvidia CUDA version from their [official website](https://developer.nvidia.com/cuda-downloads).
            - Select "Linux" -> "x86_64" -> "Ubuntu" -> "18.04" -> "runfile (local)", and download it.
            - Follow the Nvidia website installation instructions. Make sure to enable the symbolic link in `usr/local/cuda` to minimize potential future errors.
    3. **cuDNN**:
        - Ubuntu 14 or 16 ([**cuDNN 5.1**](https://developer.nvidia.com/rdp/cudnn-archive) **or 7.2**): Run `sudo ./scripts/ubuntu/install_cudnn.sh` (if Ubuntu 16 or 14 and for Graphic cards up to 10XX) or alternatively download and install it from their website.
        - Ubuntu 18 ([**cuDNN 7.5**](https://developer.nvidia.com/cudnn)): Download and install it from the [Nvidia website](https://developer.nvidia.com/cudnn).
        - In order to manually install it (any version), just unzip it and copy (merge) the contents on the CUDA folder, usually `/usr/local/cuda/` in Ubuntu and `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v8.0` in Windows.
- OpenCV must be already installed on your machine. It can be installed with `sudo apt-get install libopencv-dev`. You can also use your own compiled OpenCV version.
-  Python 3.6
-  Docker (For [Data Annotation](#step-1---data-annotation))
- Matlab R2019a (For [Data Augmentation](#step-3---data-augmentation)) 

## Required Third-Party Repositories
Before we get started, please run this in order to clone the required third party git repositories which we will use:
```
cd training
start clone_training_repos.bat [Windows]
sh clone_training_repos.sh [Linux]
```
The cloned repositories are:
- [openpose_train](https://github.com/tommarz/openpose_train) - The main training library.
- [openpose_caffe_train](https://github.com/tommarz/openpose_caffe_train) - Used by the main `openopose_train` library for the training of the model on the NVIDIA GPU.
- [coco-annotator](https://github.com/jsbroks/coco-annotator) - The annotation tool for our data.
- [openpose-plus](https://github.com/tommarz/openpose-plus) - Another training library we experienced with which is not used in this guide. If you wish to use it (although we recommend to you use the official training library this guide relates to) , please go to [this](https://github.com/roeegro/SwimmingProject/blob/master/training/OpenPose%20Plus%20Setup%20Guide.md) guide we also wrote. 

## Data Preperation and Preprocessing
In this section we will explain how we annotated our own custom data and geneterated a lmdb file so it can fit into the model. We will go through the complete pipeline.

Before we get started, create a folder with all of you images and name it `custom`. We will refer it as the `Dataset Folder` from now on but it is important to name it exactly as we stated.

### Step 1 - Data Annotation
For annotating our data we used the [coco-annotator](https://github.com/jsbroks/coco-annotator) repository which is cloned in the root directory under the name `coco-annotator`.
 We recommend you to use it as well - you can check out [this](https://github.com/roeegro/SwimmingProject/blob/master/training/Annotator-Guide.md) guide we wrote regarding installation and correct usage.

1. Use the above annotator (or any other annotator) in order to annotate your data in the [COCO Format](http://cocodataset.org/#format-data).
2.  Export the annotations file as `person_keypoints_custom.json` to the `dataset/COCO/cocoapi/annotations/` folder.
3. Copy the [dataset folder](#step-0---data-import) from step 0 to `dataset/COCO/cocoapi/images/` folder.

At the end of this step you should have:
- An annotations JSON file located in `dataset/COCO/cocoapi/annotations/person_keypoints_custom.json`
- A [dataset folder](#step-0---data-import) with the raw images located in `dataset/COCO/cocoapi/images/custom`

### Step 2 - Data Filtering and Re-indexing
In this section we will filter out some data and update the corresponding annotations JSON file accordingly.

Go to the [utils](https://github.com/roeegro/SwimmingProject/tree/master/training/utils) directory and run `json_ops.py`

By default, the [script](https://github.com/roeegro/SwimmingProject/blob/master/training/utils/json_ops.py) performs these operations on the `custom.json` annotations file in the following order:
1) Deletes redundant fields from the json structure.
2) Removes annotations with no keypoints/no segmentation, (i.e. area=0).
3) Removes images with no annotations (Those images will stay in the `dataset/COCO/cocoapi/images` folder and will be used in the next step to generate the `coco_negatives.json` file.
4) Performs re-indexing of the data so that the new indexes ranges from 1 to N where N is the number of images.
### Step 3 - Data Augmentation
For augmenting the dataset after annotating it, we used a couple of Matlab scripts located in the `training` directory which are based on the scripts from the [original](https://github.com/CMU-Perceptual-Computing-Lab/openpose_train/tree/master/training) openpose_train repository.
Those scripts rely on the [cocoapi](https://github.com/gineshidalgo99/cocoapi) repository which the original authors of OpenPose forked and modified.

Before running anything, make sure you have the `common` and `private` folders (which is located in the `training` folder) in the Matlab path.
Do expect for some errors regarding paths in to `cocoapi` 
1.  Run  `a1_coco_jsonToNegativesJson.m`  in Matlab to generate the json that contains the images with no people on them - in our case those images will be of empty pools with no swimmers in them.
2.  Run  `a2_coco_jsonToMat.m`  in Matlab to convert the annotation format from json to mat in  `dataset/COCO/mat/`.
3.  Run  `a3_coco_matToMasks.m`  in Matlab to obatin the mask images for unlabeled person. You can use 'parfor' in Matlab to speed up the code.
4.  Run  `a4_coco_matToRefinedJson.m`  to generate a json file in  `dataset/COCO/json/`  directory. The json files contain raw informations needed for training.

By the end of this step you should have a `coco_negatives.json` and `custom.json` files in the `dataset/COCO/json/` directory

### Step 4 - LMDB File Generation
The OpenPose Train repository uses the [LMDB](https://en.wikipedia.org/wiki/Lightning_Memory-Mapped_Database) library which provides a key-value database in a format of [.mdb](https://www.lifewire.com/mdb-file-2621974) file. 
In our context, the key is an id of an image and the value is the image itself along with its metadata so that the input of our training model is an LMDB file - think of it as a list of key-value pairs.
- To generate the lmdb file, run  `python c_generateLmdbs.py`  to generate the COCO and background-COCO LMDBs. The generated 
- We created a [modified LMDB reader](https://github.com/roeegro/SwimmingProject/blob/master/training/utils/lmdb_reader.py) Python module based on [this](https://gist.github.com/bearpaw/3a07f0e8904ed42f376e) git repository in order to check whether the LMDB file was generated successfuly - just run it and it should print the dimension of your data.

By the end of this step you should have `lmdb_coco` and `lmdb_background` folders in the `dataset` folder, each consists of `data.mdb` and `lock.mdb` files which represents the training data that contains at least one person and zero persons respectivly, as a LMDB file.

## Training
In this section we will walk through the training process, assuming you followed the instructions above successfully.
1) Compile our modified Caffe:
    -  Go to `training\openpose_caffe_train`
    - Make sure the `Makefile.config` is set up correctly with all correct path (By default it assumes Python2.7 without Anaconda and OpenCV 3)
    - The original config file is `Makefile.config.example` in case you want to use it or modify it. When you are done, run `cp Makefile.config.example Makefile.config` to copy it to the config file.
    -   Compile it by running:  `make all -j{num_cores} && make pycaffe -j{num_cores}`.
2) Generate the training model:
	- Go to `training\openpose_train`
	- Generate the Caffe ProtoTxt and shell file for training by running  `python d_setLayers.py`. We strongly recommend you to stick with the default setup as this one worked for us.
	    -   Set  `sCaffeFolder`  to the path of  [OpenPose Caffe Train](https://github.com/CMU-Perceptual-Computing-Lab/openpose_caffe_train).
	    -   Set  `sAddFoot`  to 1 or 0 to enable/disable combined body-foot.
	    -   Set  `sAddMpii`,  `sAddFace`  and  `sAddHands`  to 1 or 0 to enable/disable boyd mpii/face/hands (if 1, then all the above must be also 1).
	    -   Set  `sAddDome`  to 1 or 0 to enable/disable the Dome whole-body dataset (if 1, then all the above must be also 1).
	    -   Flag  `sProbabilityOnlyBackground`  fixes the percentage of images that will come from the non-people dataset (called negative dataset).
	    -   Set  `sSuperModel`  to 1 train the whole-body dataset, or to train a heavier but also more accurate body-foot dataset. Set it to 0 for the original OpenPose body-foot dataset.
	    -   Flags  `carVersion`  and  `sAddDistance`  are deprecated.
	   
3) Pre-trained weights setup:
	- Create a new directory `dataset/vgg/`
	- Download into `dataset/vgg/` 
		- The [caffemodel](http://www.robots.ox.ac.uk/~vgg/software/very_deep/caffe/VGG_ILSVRC_19_layers.caffemodel)   as  `dataset/vgg/VGG_ILSVRC_19_layers.caffemodel` 
		- The [prototxt](https://gist.githubusercontent.com/ksimonyan/3785162f95cd2d5fee77/raw/f43eeefc869d646b449aa6ce66f87bf987a1c9b5/VGG_ILSVRC_19_layers_deploy.prototxt) as `dataset/vgg/vgg_deploy.prototxt`
(Taken from this [VGG-19 model](https://gist.github.com/ksimonyan/3785162f95cd2d5fee77) page). 
The first 10 layers are used as backbone.
4) Train:
    -   Go to the auto-generated  `training_results/pose/`  directory.
    -  Run  `bash train_pose.sh` (generated by  `d_setLayers.py`) to start the training with 1 GPU
    -   Run  `bash train_pose.sh 0,1,2,3`  (generated by  `d_setLayers.py`) to start the training with the 4 GPUs (0-3).

## Training Flow
```mermaid
graph LR
A[Raw Data] 
B[Annotated Data]
C[Augmented Data]
D[Data in LMDB Format]
E[Training]
F[Trained Model]

A -- COCO Annotator --> B
B -- MATLAB --> C
C -- Python Scripts --> D
D -- OpenPose Train --> E
E -- --> F
```

## Q&A
|Error					|Reason|Solution
|-----------------------|------------------------------------|---------------|
`ImportError: dynamic module does not define module export function (PyInit__caffe)`|When trying to build the Modified Caffe Train on Anaconda enviroment |https://github.com/BVLC/caffe/issues/6054#issuecomment-375571190
|`  Could NOT find Protobuf (missing: Protobuf_INCLUDE_DIR)`|When trying to build OpenPose|https://gist.github.com/diegopacheco/cd795d36e6ebcd2537cd18174865887b
|# `Check failed: error == cudaSuccess (2 vs. 0) out of memory` | During model training | Lower batch size (We lowered from 10 to 1 on 6GB GPU (NVIDIA RTX 2060 MSI)
|`Could NOT find OpenSSL`| When installing CMake|[https://stackoverflow.com/questions/16248775/cmake-not-able-to-find-openssl-library](https://stackoverflow.com/questions/16248775/cmake-not-able-to-find-openssl-library)
| `Could NOT find Atlas (missing: Atlas_CBLAS_INCLUDE_DIR)` | When building OpenPose with CMake |https://github.com/CMU-Perceptual-Computing-Lab/openpose/issues/305
## Installation commands
- Please install the following libraries:
```
sudo apt-get install \
libprotobuf-dev=3.0.0-9.1ubuntu1 \
libleveldb-dev=1.20-2 \
libsnappy-dev=1.1.7-1 \
libopencv-dev=3.2.0+dfsg-4ubuntu0.1 
libhdf5-serial-dev=1.10.0-patch1+docs-4 \
protobuf-compiler=3.0.0-9.1ubuntu1 \
libboost-all-dev=1.65.1.0ubuntu1 \
libatlas-base-dev=3.10.3-5 \
python-numpy=1:1.13.3-2ubuntu1
```

- Install protobuf - https://askubuntu.com/questions/532701/how-can-i-install-protobuf-in-ubuntu-12-04
- Install FFMPEG - https://linuxize.com/post/how-to-install-ffmpeg-on-ubuntu-18-04/
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTIwMDIxOTIxOTYsMjU1MDg2NzIyLDYwMT
QyMzE1MiwyOTMyNTM5MzIsNDYzMzI0MzAyLDYzODg4MjMzNywx
Njg4NjE4MDldfQ==
-->