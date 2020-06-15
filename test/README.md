# SwimFix<br>Test Generator Guide 
## Table of Contents
1. [Introduction](#introduciton)
2. [Prerequisites](#prerequisites)
3. [Upload files, and Settings of Keypoints and Lines](#upload-files-and-settings-of-keypoints-and-lines)
4. [Manual Tag](#manual-tag)
	* [Tag Operation](#tag-operation)
	* [Finish and Rerun the Program with Other Input](#finish-and-rerun-the-program-with-other-input)
5. [Output Section](#output-section)
6. [CSV Input Section](#csv-input-section)
7. [CSV Output Section](#csv-output-section)

## Introduction
The following mechanism allows admin to manually annotate videos and save their annotation as csv and compare it to the OpenPose library performance.


## Prerequisites
1.  You must have Python3 installed.
2.  If you didn't run requirements.txt file of whole project, you can run in the terminal/command line the following command: `pip install -r requirements.txt`
3. Video files must be .mov format only.
4. Working with existing CSV file must be done with csvs stands in the  [input format](#csv-input-section)


## Upload files, and Settings of Keypoints and Lines

1.  Run the script by opening "test_generator.py" file.
    
2.  Press on "Load Video" button in order to load a MOV video.
    
3.  [Optional] : Press on "Load CSV" button in order to load existing csv file with keypoints [with the given format](#csv-input-section)
    
4.  [Optional] : Press on "Default Settings" in order to load the default key points and lines settings (Based on our relevant keypoints for analysis process). 

> **Note:** that in this case you will not be able to define keypoints and lines by yourself or load CSV file, so you can continue to (7)
    
5.  Insert records to body parts table. This table includes the following : Name of body part , x coordinate for current frame and y one. In this level, just type the body parts you want to include in your test. Insertion of new body part line record are done by pressing "Insert Row". Finish to do the above is done by pressing the "Finish define table" button.

    
6.  At the bottom of the window you can find drop down lists in order to define the lines between 2 body parts you want to include as line in every frame. Insertion of new line record is done by "Add" button. Finish definition the above is done by pressing "Finish line definition"
    
7.  The first frame of the loaded video is shown.
    

## Manual Tag
### Tag Operation
**![](https://lh5.googleusercontent.com/X8UDNyQpL8N7k57wK2h1wmL5CrPYGwTYB9ixQ9Mkwr2j-pvKmn_HvfHiB0E2Lgwiw1S1Zd8Fb3EiaKU0BRAPBFPbZb4WK8-e2EXBlEoYKt6nfWfHl7xnem9yffxOYTFkMA6Vh2zM)**

You can now move between the frames of the loaded movie (Prev and Next buttons).
    
Getting the key points coordinates is done as follows:

A. By default- the first body part to be taken is the first one appears in body parts list defined before, unless you defined otherwise (by pressing the desired body part row as shown in B).

B. Selection of specific body part is done by pressing the match line of your body part choice, e.g in one of the cell in this line. Pay attention that after you paint the point in this case, points measurement continues for the next body part appears in body parts list.

C. Definition coordinates of some point is done by clicking on the desired location.

> Note: When finish all frames tag of the given movie - the program will be closed.

D. Moving to the next of the previous frame is done by Next and Prev buttons respectively.
> Note: both buttons saves the information got from the current frame.

E. Clearing all coordinates of current frame is done by Clean all button.

F. Clean all button - deletes all the records of the current frame from the table, and also the points and lines in the shown frame.

**![](https://lh5.googleusercontent.com/IA-KBBZNYY5Fyh8nCksiLDbuaNR0cCFJqqlap06zfs4bD-AONcLdNmZBCJcRASXuji-w8gUH8UM5ggiP_VQYznF4tL8zXH_HyDdHphjw5s0Jjg-CB90IXg_ZEO7i1XW6Faf7pd_z)**

### Finish and Rerun the Program with Other Input
Load video button - loads other video. Working with the new video is done by following this guide again. 
> Important Note : choosing this option will delete accumulated data. Make sure you saved the data you generated before!

> Important Note : Clicking the red button will also delete accumulated data. Make sure you saved the data you generated before.

H. Save button - Saves all the data generate until the current working stage. See [output section](#output-section).

## Output Section:

The following files are saved as an output of the program in the working directory (e.g in test folder):

1.  .MOV file named by the given file with the wireframe annotation according to your manual tag.
2.  .CSV file with the key points coordinated you signed before for each frame. Please read CSV Output section.

## CSV Input Section:

There is an expected format for the csv file. The csv must include the following columns : 

    Frame Number , <body_part>* s.t <body_part> := <body_part>_X , <body_part>_Y

## CSV Output Section:

The CSV output format is as follows: You will have for each frame number the X and Y coordinated for each body part mentioned in body parts table in the program.
