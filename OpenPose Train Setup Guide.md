<center>OpenPose Train Setup Guide</center>
=================================
## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Data Preperation and Preprocessing](#data-preperation-and-preprocessing)
	- [Data Import](#step-0---data-import)
	- [Data Annotation](#step-1---data-annotation)
	- [Data Augmentation](#step-2---data-augmentation)
	- [LMDB File Generation](#step-3---lmdb-file-generation)
4. [Training](#training)
5. [Validation](#validation)
6. [Testing](#testing)
## Introduction
This is a complete guide for setting up the [OpenPose Train]((https://github.com/CMU-Perceptual-Computing-Lab/openpose_train))  which is used alongside the [original](https://github.com/CMU-Perceptual-Computing-Lab/openpose) OpenPose library in our [Swimming Project](https://github.com/roeegro/SwimmingProject).
For our project, we modified some of the files in the original repository so we created a [fork](https://github.com/tommarz/openpose_train) with the updated files which you will work with.
Throughout this guide we will walk through all the required steps for training a custom model on your own data, top to bottom.
From now on the `openpose_train` directory will be our working directory and the `SwimmingProject` directory which is the main directory of our git repository will be our root directory.
> **Note**: This guide is related on training a model on a COCO formatted custom data **only**. 
>  In case you want to train a model just on the COCO dataset rather than your own, please follow the original repository instructions. You can read more about the COCO dataset which the OpenPose default COCO model was trained on [here](http://cocodataset.org/).
### Disclaimer
This guide is based on a setup we successfully managed to perform on an AWS EC2 virtual machine with the following AMI:<br>**Deep Learning Base AMI (Ubuntu 18.04) Version 22.0 (ami-0f6127e61a87f8677)** (more details  [here](https://aws.amazon.com/marketplace/pp/B07Y3VDBNS?qid=1589717278223&sr=0-1&ref_=srh_res_product_title))
Keep in mind that this machine is delivered with all the NVIDIA related prerequesities that are mandatory for both OpenPose training and inference versions (The full list of prerequesities for the inference version is [here](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/prerequisites.md))
This means the guide assumes you are running on a a similiar machine.
## Prerequisites
Make sure you have those and before continuing:
- Nvidia GPU version prerequisites:
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
- All the required git repositories must be cloned in the root folder. Please clone those by running `clone_training_repos.bat` or `clone_training_repos.sh`  from the command line/terminal.
- Python 3.6
## Data Preperation and Preprocessing
In this section we will explain how we annotated our own custom data and geneterated a lmdb file so it can fit into the model. We will go through the complete pipeline.
>**Note:** For this section and this section **only** we used a Windows 10 machine with:
>- Docker (For [Data Annotation](#step-1---data-annotation))
>- Matlab R2019a (For [Data Augmentation](#step-2---data-augmentation)) 
>- Python 3.6 installed (For [LMDB File Generation](#step-3---lmdb-file-generation))
>
>In case you are are using Ubuntu you may not need a Docker for the annotation and Matlab for the augmentation.

### Step 0 - Data import
Before we get started, create a folder with all of you images and name it `custom`. We will refer it as the `Dataset Folder` from now on but it is important to name it exactly as we stated.

### Step 1 - Data Annotation
For annotating our data we used the [coco-annotator](https://github.com/jsbroks/coco-annotator) repository which is cloned in the root directory under the name `coco-annotator`

1. Use the above annotator in order to annotate your data in the correct format.<br>Please check out [this](https://docs.google.com/document/d/1CnZHzUDVSLxYTczuYnHGJrh37uqOqPRSNcRDbleLI5w/edit?usp=sharing) guide we wrote regarding installation and correct usage.
2.  Export the annotated data to a JSON file in a [COCO Format](http://cocodataset.org/#format-data) to `dataset/COCO/cocoapi/annotations/` folder and name it `person_keypoints_custom.json` .
3. Copy the [dataset folder](#step-0---data-import) from step 0 to `dataset/COCO/cocoapi/images/` folder.

At the end of this step you should have:
- An annotations JSON file located in `dataset/COCO/cocoapi/annotations/person_keypoints_custom.json`
- A [dataset folder](#step-0---data-import) with the raw images located in `dataset/COCO/cocoapi/images/custom`

### Step 2 - Data Augmentation
For augmenting the dataset after annotating it, we used a couple of Matlab scripts located in the `training` directory which are based on the scripts from the [original](https://github.com/CMU-Perceptual-Computing-Lab/openpose_train/tree/master/training) openpose_train repository.
Before running anything, make sure you have the `common` folder (which is located in the `training` folder) in the Matlab path.
1. Place the [dataset folder](#step-0---data-import) in the `dataset/COCO/cocoapi/images/`  folder if you havn't done so yet.
2.  Run  `a1_coco_jsonToNegativesJson.m`  in Matlab to generate the LMDB with the images with no people on them.
3.  Run  `a2_coco_jsonToMat.m`  in Matlab to convert the annotation format from json to mat in  `dataset/COCO/mat/`.
4.  Run  `a3_coco_matToMasks.m`  in Matlab to obatin the mask images for unlabeled person. You can use 'parfor' in Matlab to speed up the code.
5.  Run  `a4_coco_matToRefinedJson.m`  to generate a json file in  `dataset/COCO/json/`  directory. The json files contain raw informations needed for training.

By the end of this step you should have a `coco_negatives.json` and `custom.json` files in the `dataset/COCO/json/` directory

### Step 3 - LMDB File Generation
The OpenPose Train repository uses the [LMDB](https://en.wikipedia.org/wiki/Lightning_Memory-Mapped_Database) library which provides a key-value database in a format of [.mdb](https://www.lifewire.com/mdb-file-2621974) file. 
In our context, the key is an id of an image and the value is the image itself along with its metadata so that the input of our training model is an LMDB file - think of it as a list of key-value pairs.
- To generate the lmdb file, run  `python c_generateLmdbs.py`  to generate the COCO and background-COCO LMDBs. The generated 
- We created a modified LMDB reader Python module based on [this](https://gist.github.com/bearpaw/3a07f0e8904ed42f376e) git repository in order to check whether the LMDB file was generated successfuly. It is located in the `SwimmingProject\utils` folder under the name `lmdb_reader.py`

By the end of this step you should have `lmdb_coco` and `lmdb_background` folders in the `dataset` folder, each consists of `data.mdb` and `lock.mdb` files which represents the training data that contains at least one person and zero persons respectivly, as a LMDB file.

## Training
In this section we will walk through the training process, assuming you followed the instructions above successfully.
1) Download and compile our modified Caffe:
    -   OpenPose Caffe Training:  [github.com/CMU-Perceptual-Computing-Lab/openpose_caffe_train](https://github.com/CMU-Perceptual-Computing-Lab/openpose_caffe_train).
    -   Compile it by running:  `make all -j{num_cores} && make pycaffe -j{num_cores}`.
2) Generate the Caffe ProtoTxt and shell file for training by running  `python d_setLayers.py`.
    -   Set  `sCaffeFolder`  to the path of  [OpenPose Caffe Train](https://github.com/CMU-Perceptual-Computing-Lab/openpose_caffe_train).
    -   Set  `sAddFoot`  to 1 or 0 to enable/disable combined body-foot.
    -   Set  `sAddMpii`,  `sAddFace`  and  `sAddHands`  to 1 or 0 to enable/disable boyd mpii/face/hands (if 1, then all the above must be also 1).
    -   Set  `sAddDome`  to 1 or 0 to enable/disable the Dome whole-body dataset (if 1, then all the above must be also 1).
    -   Flag  `sProbabilityOnlyBackground`  fixes the percentage of images that will come from the non-people dataset (called negative dataset).
    -   Sett  `sSuperModel`  to 1 train the whole-body dataset, or to train a heavier but also more accurate body-foot dataset. Set it to 0 for the original OpenPose body-foot dataset.
    -   Flags  `carVersion`  and  `sAddDistance`  are deprecated.
3) Download the pretrained  [VGG-19 model](https://gist.github.com/ksimonyan/3785162f95cd2d5fee77)  and unzip it into  `dataset/vgg/`  as  `dataset/vgg/VGG_ILSVRC_19_layers.caffemodel`  and  `dataset/vgg/vgg_deploy.prototxt`. The first 10 layers are used as backbone.
4) Train:
    -   Go to the auto-generated  `training_results/pose/`  directory.
    -   Run  `bash train_pose.sh 0,1,2,3`  (generated by  `d_setLayers.py`) to start the training with the 4 GPUs (0-3).

## Validation

## Testing

# Markdown extensions

StackEdit extends the standard Markdown syntax by adding extra **Markdown extensions**, providing you with some nice features.

> **ProTip:** You can disable any **Markdown extension** in the **File properties** dialog.


## SmartyPants

SmartyPants converts ASCII punctuation characters into "smart" typographic punctuation HTML entities. For example:

|                |ASCII                          |HTML                         |
|----------------|-------------------------------|-----------------------------|
|Single backticks|`'Isn't this fun?'`            |'Isn't this fun?'            |
|Quotes          |`"Isn't this fun?"`            |"Isn't this fun?"            |
|Dashes          |`-- is en-dash, --- is em-dash`|-- is en-dash, --- is em-dash|


## KaTeX

You can render LaTeX mathematical expressions using [KaTeX](https://khan.github.io/KaTeX/):

The *Gamma function* satisfying $\Gamma(n) = (n-1)!\quad\forall n\in\mathbb N$ is via the Euler integral

$$
\Gamma(z) = \int_0^\infty t^{z-1}e^{-t}dt\,.
$$

> You can find more information about **LaTeX** mathematical expressions [here](http://meta.math.stackexchange.com/questions/5020/mathjax-basic-tutorial-and-quick-reference).


## UML diagrams

You can render UML diagrams using [Mermaid](https://mermaidjs.github.io/). For example, this will produce a sequence diagram:

```mermaid
sequenceDiagram
Alice ->> Bob: Hello Bob, how are you?
Bob-->>John: How about you John?
Bob--x Alice: I am good thanks!
Bob-x John: I am good thanks!
Note right of John: Bob thinks a long<br/>long time, so long<br/>that the text does<br/>not fit on a row.

Bob-->Alice: Checking with John...
Alice->John: Yes... John, how are you?
```

And this will produce a flow chart:

```mermaid
graph LR
A[Square Rect] -- Link text --> B((Circle))
A --> C(Round Rect)
B --> D{Rhombus}
C --> D
```
<!--stackedit_data:
eyJoaXN0b3J5IjpbMTc3OTc3Nzg2MV19
-->