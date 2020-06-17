
# SwimFix<br>Test Generator Guide 
## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Upload files, and Settings of Keypoints and Lines](#upload-files-and-settings-of-keypoints-and-lines)
4. [Manual Annotation](#manual-annotation)
	* [Annotating Frame](#annotating-frame)
	* [Finish and Rerun the Program with Other Input](#finish-and-rerun-the-program-with-other-input)
1.  [CSV Input Format](#csv-input-format)
5. [Output Format](#output)
7. [CSV Output Format](#csv-output-format)

## Introduction
The following mechanism allows admin to manually annotate videos and save their annotation as csv and compare it to the OpenPose library performance.


## Prerequisites
1.  You must have Python3 installed.
2.  Run in the terminal/command line from the `/testing` directory the following command: `pip install -r requirements.txt`
3. Video files must be .mov format only.
4. Working with existing CSV files must be done with csvs stand in the  [input format](#csv-input-format)


## Upload files, and Settings of Keypoints and Lines

1. Run in the terminal/command line from the `/testing` directory the following command `python test_generator.py`.
    
2.  Press on "Load Video" button in order to load a MOV video.
    
3.  [Optional] : Press on "Load CSV" button in order to load existing csv file with keypoints [with the given format](#csv-input-format)
    
4.  [Optional] : Press on "Default Settings" in order to load the default key points and lines settings (Based on our relevant keypoints for analysis process). 

> **Note:** In this case you will not be able to define keypoints and lines by yourself or load CSV file, so you can continue to (7)
    
5.  Insert records to body parts table. This table includes the following : Name of body part , x coordinate for current frame and y one.<br> In this level, just type the body parts you want to include in your test. Insertion of new body part line record are done by pressing "Insert Row".<br> Applying is done by pressing the "Finish define table" button.

    
6.  At the bottom of the window you can find a drop down list to define lines between 2 body parts you want to include as a line in every frame. Insertion of new line record is done by the "Add" button. <br>Applying is done by pressing "Finish line definition" button.
    
7.  If all the steps above were done right- the first frame of the loaded video should appear.
    

## Manual Annotation
### Annotating frame
**![](https://lh5.googleusercontent.com/X8UDNyQpL8N7k57wK2h1wmL5CrPYGwTYB9ixQ9Mkwr2j-pvKmn_HvfHiB0E2Lgwiw1S1Zd8Fb3EiaKU0BRAPBFPbZb4WK8-e2EXBlEoYKt6nfWfHl7xnem9yffxOYTFkMA6Vh2zM)**

You can now move between the frames of the loaded movie (Prev and Next buttons).
    
Getting the keypoints coordinates is done as follows:

A. By default- the first body part to be taken is the first one appears in the body parts list defined before, unless you have defined otherwise (by pressing the desired body part row as shown in B).

B. Selection of a specific keypoint is done by selecting the corresponding line of the desired keypoint.

C. Annotating a keypoint is done by clicking on the desired location on the frame.
 >**Note 1**: By default,  the next keypoint to be annotated is the one appears next on the keypoints list.
> **Note 2**: Once finished annotating all frames of a given movie - the tool will be closed automatically.

D. Moving to the next or the previous frame is done by "Next" and "Prev" buttons respectively.
> Note: both buttons saves the information got from the current frame.

E. Clearing the last annotation is done by pressing "Undo" button.

F. Clearing all the annotations of the current frame is done by pressing "Clean all" button.

**![](https://lh5.googleusercontent.com/IA-KBBZNYY5Fyh8nCksiLDbuaNR0cCFJqqlap06zfs4bD-AONcLdNmZBCJcRASXuji-w8gUH8UM5ggiP_VQYznF4tL8zXH_HyDdHphjw5s0Jjg-CB90IXg_ZEO7i1XW6Faf7pd_z)**

### Finish and Rerun the Program with Other Input
"Load video" button - loads other video. Working with the new video is done by following this guide again. 
> **Important Note 1**: choosing this option will delete accumulated data. Make sure you saved the data you generated before!
> **Important Note  2**: Clicking the red "X" button will terminate the tool and also delete accumulated data. Make sure you saved the data you generated before!

H. Save button - Saves all the generated annotation up to this point. See [output](#output) section.


## CSV Input Format

There is an expected format for the csv file. The csv must include the following columns : 

    Frame Number , <body_part>* s.t <body_part> := <body_part>_X , <body_part>_Y


## Output

The following files are saved as an output of the program in the working directory (i.e in test folder):<br>

1. A  file in a MOV format named by the given file with the keypoints annotations according to your manual annotations.
2.  A  file in a CSV format with the keypoints coordinates you annotated for each frame. Please read [CSV Output](#csv-output-format) section.

### CSV Output Format

The CSV output format is as follows: You will have for each frame number the X and Y coordinated for each body part mentioned in body parts table in the program.
