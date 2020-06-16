

# <center> SwimFix Maintenance Guide</center>

## Table of Contents
1. [Introduction](#introduction)
2. [Client Side](#client-side)
	* [Routes File](#routes-file)
	* [Gui Utils](#gui-utils)
	* [Directory and Files Management](#directory-and-files-management)
	* [Video Cutter](#video-cutter)
	* [Requests Format](#requests-format)
4. [Server Side](#server-side)
	* [Request Parser File](#client-request-parser-file)
	* [Facade Module](#facade-module)
	* [Data Extractor Module](#data-extractor-module)
		* [Functionality](#functionality)
		* [Algorithms](#algorithms)
	* [Data_Analyser Module](#data_analyser-module)
	* [Visualizer Module](#visualizer-module)
	* [Evaluator Module](#evaluator-module)
		 * [Functionality](#functionality)
		* [Error Detection Algorithms](#error-detection-algorithms)
		* [Scoring Method](#scoring-method)
		* [Plug and Play](#plug-and-play)
	* [Tester Module](#tester-module)
	* [Output Manager Module](#output-manager-module)
	* [Utils](#utils)
	*  [File Management](#file-management)
	* [Data Base Structure](#data-base-structure)
5. [Adding Functionality Schema](#adding-functionality-schema)
6. [Assimilation on New Device and Run All Program](#assimilation-on-new-device-and-run-all-program)

## Introduction
Our system has 4 main parts. The first one is the training infrastructure.
For more details, [click here](https://github.com/roeegro/SwimFix/tree/master/training).
The second one is the test generator module, where user can produce ground truth csvs. For more details, [click here]([https://github.com/roeegro/SwimFix/tree/master/test](https://github.com/roeegro/SwimFix/tree/master/test)).

The other 2 parts are used for the SwimFix web application and they include a web client part and a server for analysis and evaluation. Both parts written in Python and connect each other with TCP conneciton.


## Client Side
The client side is a web interface which supports 2 types of users : usual and admin ones. Usual user interface supports upload of video to the server (for analysis), view data and feedback about technique of previous swimming videos (including error description and final score), and also participate in forum.
Admin users can also add tests and run them in the system in order to examine system's performance. More details about the user interface can be found in this [link](https://github.com/roeegro/SwimFix/tree/master/client).
We used Flask, a python web framework, to write the client side. This library enables the developers to load dynamically web pages with python code, define relations between pages, and even pass parameters from python code to html one.

**![](https://lh4.googleusercontent.com/pdX746XNbQLlHE_6zDMXXP7rpbMgTFroraBN8xC-R3Qnm78W9YiKm30DgKCjz8rehIAaTdKNiCdZUZo5CGQkyQ7c2Sndu6k4DMRUiXpNyHQ4VMTcAhmrD847jSxLGj2dGtI3_lvd)**

### Routes File
This is the most important module in the client side. It defines the web links of all the pages and binds them to the relevant html page (appears in templates directory). For each html page, there must be found a function in this .py file which looks as follows:

    @app.route('/', methods=['GET', 'POST'])  # only for home page definition
    @app.route("/<page-name>", methods=['GET', 'POST'])  
    def page_name():
		    <some code>  
           return render_template('page-name.html')

The first line denotes that the next url address is the home page of the site, and it should be placed to this page only. The methods specify the type of requests supported in this page.
The second line binds between the url address to the function below.
In the function there is a code, that frequently connects to the server in order to send requests or/and get responses.
Each function must return a redirection to some html page to be loaded in the browser.
You can pass other arguments to the respective html code by specifying them as follows

    return render_template('page-name.html',param1 = argument1,...)
Using this arguments in the respective html code is done as follows

    {{parameter name}}

> **Note**: Url address definition, function name and html page redirection returned in the end of the function name must be consistent, correlative and named by html and python conventions respectively.

Another important service supplied by this module is handling waiting pages in order to give the client indication for the progress of upload and analyse the video. The functions that deals with handling with this functionality are:

1. `load_video, run_test` -  python code relevant to the pages where waiting page are shown. In this function we create new thread running the waiting page code defined in function `receive_openpose_msg` .
2. `receive_openpose_msg`  - uses global sockets which used for connecting the server and getting from it a 1 byte code signifies the stage of analysis. Pay attention for the dictionary `response_dict` which map between server code to the message shown in the waiting page. If the code got from the server is code for finish the process, it waits for another message in size of 1024 bytes  signifies whether the process succeeded or not, and changes its status for updating the page shown in the screen (See next function).
3. `thread_status` -  called frequently from `waiting-page.html`(in templates folder), for checking thread status. Returns to the html the status, and if the status is "finished" the html redirects to other page (with jquery).


### Gui Utils
A small module with some functions for files manipulation such as extracting data from zip file got from server, getting specific files from zip, convert csv content to list of dictionaries passed to the server.

 ### Directory and Files Management
 
 **temp -** Contains zip files with information hold in the server, and some temporal folder which holds files to be shown in the browser.
> Note: When asking for feedback or data of specific video, the zip is downloaded to this directory. For more details of getting feedbacks and data, please click [here](https://github.com/roeegro/SwimFix/tree/master/client#watching-feedbacks-on-videos).
 
**partial_movies -** Generated by the code and contains intervals of movies to be uploaded to the server. See video trimmer section for more details, [Video Cutter ](#video-cutter)

**uploaded_files  -** Generated by the code and contains videos uploaded before from the machine the user works on.

**static -** Contains temp directory and also css, js files, images and other files that are loaded or shown in the html pages shown in temp directory.

#### chart-area-js-demo.js
Important js file is chart-area-js-demo.js ( appears in static/js/demo/chart-area-js-demo.js), which has the following responsibilities: 
 1. This file has functions taking csv file (located in [temp directory](https://github.com/roeegro/SwimFix/blob/master/MaintenanceGuide_new.md#directory-management)), reads it into map object, parse this object in order to show graphs using chart.js library dynamically. Graphs positions is done by working with document elements, and definition of visibility and events (showing the frame matched to point position in the graph) is done with Chart object.
 2. Frame view - When pressing on points in the graph, the frame is changed to the match frame. This done by taking the position of the point in the x-axis and getting the relevant frames stored in (located in [temp directory](https://github.com/roeegro/SwimFix/blob/master/MaintenanceGuide_new.md#directory-management)).
 The relevant functions handling with those events are setImage and drawImage and loadImage (they have the same described functionality, but the second one binds an event to the load image of painting manual fixes on the current frame).
 
This js file is used by all the pages shown feedbacks (e.g user-feedback.html, previous-feedback.html, and test-results.html).

**templates -** Contains html code that are loaded by the Flask code as shown in the section above.

### Video Cutter 
A module for cutting out only the relevant parts from a swimmer's video- which are the parts where the swimmer is big enough for us to recognize his body parts, and where he is swimming towards the camera; we are not interested in the parts in which the pool is empty or when the swimmer is swimming away from the camera. We want to minimize the data sent to the server in order to save time analyzing a video on the server.<br>The main function in this module is `video_cutter`, which works according to few parameters:
<br>`min_area`- motion sensitivity factor - contour area wise
<br>`pixel thresh`- pixel sensitivity factor - the change of a pixel <br>
`undetected_frames_thresh` - number of frames with no motion detected in it which above it a video part is defined irrelevant.
<br>`omit_clips_below` - minimum length of a video part to be considered relevant.<br>
 Additional parameter for debugging is `debug_mode` - a `true` value will provide you visual feedback and prints in the command line while running this function.<br> This parameters are tuned according to few swimming videos and the results of the parameters we tried can be found in Preprocessor_param_tuning .xlsx< link ><break>
The output of this function is 1 or more video in the directory mentioned in the variable `output_dir` under the name <br>`<original video name>_from_frame_<the frame number this part was cutted from>.mp4`<break>
>More about the algorithm can be found in the comments of the file [preprocessor.py](https://github.com/roeegro/SwimFix/blob/master/client/src/preprocessor.py).


### Requests Format
In order to connect to the server, TCP connection is handled for each request. There are different types of requests but they all have the same general format.

    < Request Type > (< parameter name >: < argument name >)*

Handling those requests in server side are described in this section [Request Parser File](#client-request-parser-file)


## Server Side

The main responsibilities of the server is : 
* Parsing requests from client side. see [Request Parser File](#client-request-parser-file)
* Extracting key points of swimmer in the video.
* Processing the data extracted from video.
* Using the data to get analytics data for evaluation metrics measuring swimmer technique.
* Management of files.
* Returning responses to the client side. 

### Client Request Parser File
This module is the gate for using functionalities of the server. 
The parser takes the first word in the request, and redirect the request to the matching handler function, with a dictionary binds between the first word and the matching handler as shown:

    requests_dict = {'login': login, 'register': register, 'view_feedbacks_list': view_feedbacks_list,  
      'view_graphs': view_graphs,  
      'forum_view_page': forum_view_page, 'forum_view_topic': forum_view_topic,  
      'forum_topic_name': forum_topic_name,  
      'forum_create_topic': forum_create_topic, 'forum_create_post': forum_create_post, 'add_test': add_test,  
      'run_test': run_test, 'upload': upload, 'upload_image_fix': upload_image_fix,  
      'view_tests_list': view_tests_list, 'view_test_results': view_test_results}

### Facade Module
This module is an API of the server's functionality, so each function in this module supplies abstraction of levels in data processing. For example the function `get_angles_csv_from_keypoints_csv` takes a csv file with all coordinates of body part and generates csv file with angles by generate vector file, then evaluates the angles from the vector file.

### Data Extractor Module
This module is the first level in data extraction. Its goal is to extract basic information about body parts coordinates and then process them.
Since the system analyses rowing swimming style the body parts detected are: nose,neck,right shoulder, right elbow, right wrist, left shoulder, left elbow, and left wrist (indexed by points 0-7). 
In addition, the process finds vectors defined by the points in the skeleton and their directions are defined by the arrows in the figure below. 
The process also calculates the angles between the body parts defined in the figure:
a - Global right shoulder angle
b - Right shoulder angle.
c - Global right arm angle
d - Right elbow angle
e - Global right forearm angle.
f - Global left shoulder angle
g - Left shoulder angle.
h - Global left arm angle
i - Left elbow angle
j - Global left forearm angle.

<p align="center">

<img src=https://lh5.googleusercontent.com/sr14FSTG-eyOk8JKLQq3TOxGkVSqYeH9QnM2cK1v8Hlv4QhHqsvtC3bNyT9RBRLQQTkXuNn6GSgR6KMNtYbsxLzkiRERfCBMyLaOh0gh6joM8Y_K5ufO_AS4XmKBRv8-Lt3j1DiQ>

For more information about the wire frame structure and the output of OpenPose, please check the official [output](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/output.md)  doc.<br>
</p>

#### Functionality
Main functionality supported in this module:

1. `get_keypoints_csv_from_video` 
	function is the first stage in data extraction of video. It receives path to video, and argument named `params` - dictionary which can holds some of OpenPose configurations. The output is a path to csv file named `all _keypoints` with the following format:
rows - for each frame
columns - each body part we have 3 columns : < Body Part >X , < Body Part >Y, < Body Part >Score.
X,Y stands for the coordinates of the specific body part, and Score stands for the confidence score of OpenPose for its estimation.
If the body part appears in hand so we have those 3 columns for each side. We specifying it by L/R (left or right) letter before the body part name.
Those are the columns: 
`[Frame Number,NoseX,NoseY,NoseScore,NeckX,NeckY,RElbowY,RElbowScore,RWristX,RWristY,RWristScore,LShoulderX,LShoulderY,LShoulderScore,
LElbowX,LElbowY,LElbowScore,LWristX,LWristY,LWristScore]`

2. `filter_and_interpolate`
	This is the second stage in data extraction process. This function takes the csv path returned from the first function, and filters records with noises and inaccuracies. For the algorithm use [clicke here](#algorithmns) .If there are closer intervals with high score, the function completes the gap between the intervals by interpolation. Returns path to updated body parts coordinates.

3. `generate_vectors_csv`
	This is the third stage in data extraction process. This function takes the path given in the second function, extracted in the function above, and returns a path to csv file generated in the function, includes the vectors.
	This csv contains rows for each frame, and columns describes the vectors by X,Y coordinates.
	As shown in the skeleton image, the vectors we looks for are: right chest, left chest, right arm, left arm, right forearm, left forearm. The columns format is similar to the format described in the first function in this module.

4. `generate_angles_csv` The last stage in data extraction process. This function takes a path to the vectors csv file got from the function above and calculate the angles between 2 relevant vectors. The format of the csv file is similar to the csvs above and includes for each frame the following angles: right shoulder angle, left shoulder angle, right elbow angle, left elbow angle, righat global shoulder angle , left global shoulder angle ,right global elbow angle and left global elbow angle.

5. There are more helper functions which are called by one or more of the functions above. Some of those functions are used for calculation or some intermediate stages in one of the functions above. Documentation for each function in data_extractor module is found in the code.

#### Algorithms
**Filter and Interpolate algorithm (all keypoints csv path):**
This algorithm runs for the following body-parts: neck , nose, right shoulder, left shoulder, (right elbow and wrist together, considering elbow score), and (right elbow and wrist together, considering elbow score):
1. Get intervals of at least x (by default 3) frames placed in sequence with body part score higher then threshold ( set to be 0,4 by default).
2. Filter body-part coordinates data for frames which are not in the mentioned intervals.
3. Merge between adjacent intervals with at most distance d (where d defined to be 10 by default).
4. Try to extend each intervals by interval extension algorithm.
For neck only
5. Run neck pose-estimator algorithm.

**Interval Extension Algorithm (interval, body-part):**
1. Calculate average change of Y coordinate of body part in the given interval.
2. Go over the next and the previous frames in relation to the interval and check if the change of frame body-part-Y coordinate in relation to next/previous respectively include it in the interval. 

**Neck Pose Estimator Algorithm (all keypoints csv path):**
1. For each frame:
     A. If neck (X and Y) known - continue to the next frame.
     B. If both shoulders are known - neck x,y coordinates are the average
 2. Find known intervals for right shoulder.
 3. For each interval (if it is possible) - calculate the location of the missing data of neck with linear interpolation over the specific interval.
 4.  Find known intervals for left shoulder.
 5. For each interval (if it is possible) - calculate the location of the missing data of neck with linear interpolation over the specific interval.

### Data_Analyser Module

This module should be operated after all stages in data_extractor are finished, This module should calculate advanced measures derived from the coordinates, vectors and angles csv files generated before.
This module is able to calculate:
*  Average time period
* Average angle for each angle.

### Visualizer Module
 This module plot figures derived from csvs generated in other module.
 In each function in this module, you can control the output file name, the location of this file, which columns will be export into figure, and even how to define the x-axis in the figures. This module enables the developer even to plot multifigures based on the same csvs and even comparison figures based on csv files with the same structure (e.g columns names).

 ### Evaluator Module
#### Functionality
This module gets as an input paths to the body part coordinates after filter and path to csv contains the angles calculated before, and operates each function inside this module and each function defines in plug and play < link >, in order to detect errors of technique of the filmed swimmer. The main function of this module is `perfomance_evaluator`.
At the bottom of the module there is a list of functions (for inner module functions which defined before), and strings (for plug and play files which are added in the first for	loop in the main function) to be executed, and the main function of this module runs over this list and activate each function/call to the relevant file respectively with the paths specified above.
> **Note**: Each file in plug and play is called with the paths and with some other arguments relevant for consistency of information to be accumulated during the runtime of this module over all the error detection function - whereas they defined before inside the module, or by plug and play functions.

The output of this module is 2 csv files (and grade). The first one keeps an id of error and its description, based on the dictionary explained before. The second one includes for each error type defined in the module: the id, and list of frames where the specific error detected. The files above are saved in the directory of current upload. Read [output path hierarchy](#output) for more information about the output hierarchy and the files it includes.
> **Note**: Each function name and the relevant description entry in the dictionary must be named as follows:
	> Function name : check_if_< error description with underscores between words>
	Description match to this error must be the description above with spaces seperated between the words (instead of the underscores before).

#### Error Detection Algorithms
> Notes:
>* All the algorithms below are found in the module and defined by Dr. Raziel Riemer - one of the entrepreneurs of the project, and bio-mechanic expert.
>* All the algorithms receive as an input 2 paths to the keypoints and angles csvs, if not mentioned otherwise.
>* In the code, the algorithms are activated for right and left hand separately, but written here generality to make it easier to read and understand.

**Check if hand crossed the neck line:**
1. For each frame:
A. calculate x coordinate of palm.
B. If (x coordinate of right palm bigger than x coordinate of neck) or (x coordinate of left palm smaller than x coordinate of neck) - sign as error and draw line from neck down to the palm to emphasis the error.

**Calculate palm x coordinate (elbow x coordinate, wrist x coordinate):**
Use the formula : 0.37 * (elbow x coordinate - wrist x coordinate) + elbow x coordinate

**Check if elbow angle is out of range\* :**

1. if angle > max angle or angle < min angle:
	A. Sign this frame as an error.
	B. Draw 2 lines emphasis the position of wrist when angle is the max and min angle for emphasis the position range.

* min angle = 90, max angle = 175 (When elbows almost lock)

**Check if global wrist angle is out of range\* :**
Inner angle - the angle directs to the body
External angle - the angle directs outside the body.

1. if inner or outer angle > max inner or outer angle respectively:
	A. Sign this frame as an error.
	B. Draw 2 lines of the max inner and outer angles, for emphasis the recommended range of wrist position.

* Max inner angle = 45, Max external angle is 10.

#### Scoring Method
Defined for each function and makes it more flexible to define scoring method separately for each type of error and even for single instance of this error.
For now we defined the cost of each error to be 1.5 points. Score range is in scale of 0-100. 

#### Plug and Play
This feature supplies the ability for developers to add new swimming errors definitions (and their weights) for future analysis.
Feature use is done by writing separated .py files without disable server's running, and sending the files to the server when they are ready.
Once the user sent those functions from the client side, they are stored in [plug_and_play_functions](#plug_and_play_functions) directory.
Those files will be executed when error evaluation will be done to swimmer's video within evaluator module.
In order to use this feature correctly, the project authors defined a format for writing such an external functions. The format is as follows:
File naming: `check_if_< your new error description >`
Content:

    import evaluator # for using its functions.
    def check_if_< your new error description >(all_kp_df, angles_df, name, side,error_names,errors_df):
	    if side not in ['L', 'R']: # make sure you explore right and left side of the swimmer's body and not something else.
	        return
	    error_id = evaluator.get_id_of_error(name,error_names_for_external_calling = error_names)
	    for index, __ in all_kp_df.iterrows()/angles_df.iterrows():
	    < your error detection code >
	    if error_id != -1 and index not in errors_df['frames'][error_id]:
	    error_weight  += <some formula for error weight>
	    errors_df['frames'][error_id] =  errors_df['frames'][error_id] + [index] # Join this frame to frames which this error already detected.
	    errors_df['points_reduced'][error_id] =  errors_df['points_reduced'][error_id] +  error_weight # Accumulate points reduced for this error, for user view.

 
	check_if_< your new error description >(all_kp_df, angles_df, name, side,error_names,errors_df) # function activation
    
    
 > **Note 1**: Disable of plug-and-play function execution is done by removing the matching .py file from the directory mentioned above. 

 > **Note 2**: You may want to annotate your error emphasis. You can do it with the function:
 > `evaluator.draw_line(index, (from_x_coor,from_y_coor), (to_x_coor,to_y_coor),color)`, a function written in evaluator which draw lines between defined points and stores the results in the 
[swimfix_annotated_frames directory](#output), where color is in BGR format (this function uses [cv2.line](https://docs.opencv.org/2.4/modules/core/doc/drawing_functions.html) function).

 > **Note 3**: Make this function fit to error detection of both hands. 

### Tester Module
This module has some responsibilities: 
1. Comparing csv files with the same format, and used to compare manual annotations vs. automatic annotation returned from the [Data Extractor Module](#data-extractor-module), This module generates csv files comparing each column and plotting figures based on the new csv files to emphasis and visualize the gap between the manual annotations and the automatic ones. By activating this module we can measure the performance of the system.
 > **Note**: You can activate Tester module by calling
 > Tester.start_test(actual_csvs_dir, expected_csvs_dir, output_path, filename), only after you insured you have expected data for this video (see [Expected Data](#expected_data)), and after you call to all functions in [Data Extractor Module](#data-extractor-module). Our implementation automatically does the described steps before run the test itself (See implementation in client_request_parser in function run_test).

2. Calculating loss value for each comparison csv file for measurement of the accuracy of our angles extractor algorithm related to the angles extracted from ground truth csvs, which we have for some movies.
3. (???????????????????????????????????????????????) - Comparing errors which were derived from our extracted data with errors derived from ground truth data. 

### Output Manager Module
This module purpose is to build dynamically folders which are necessary for data storage and create each upload and supply easy access to directories in order to store the generated files dynamically.
This module uses dictionary that maps between a name of desired path to its actual path in the [output path hierarchy](#output).
The output manager also enables you to know if there is a ground_truth file in expected data [Expected Data](#expected_data), and also builds environment to locate the test results in. See [Tester Module](#tester-module) for more details.

### Utils
Simple module with operations on path, names. Its also holding variable with constant values for our system (like body parts detected, etc.)

### File Management
 
The server side includes some directories for files management.

#### Videos
each video sent to the server is stored in this directory for future use of the developers.

#### Temp
Stores zip files containing relevant content for user's request. Those files sent to the client side and stored in `/client/src/static/temp` on the client side.
#### Expected_data
Stores csvs that created by the manual tag defined in [test generator](https://github.com/roeegro/SwimFix/tree/master/test) part. The tester module search for the ground truth of given video and comparing this csv file and the data derived from it to the data that our system produces.


#### OpenPose

This directory is not exist in the repository but should be added by the developer to the server side directory. This directory should contain the binaries necessary for execution of this pose estimation library's code. Please see this [link](https://github.com/CMU-Perceptual-Computing-Lab/openpose) in order to build OpenPose on your machine. After building OpenPose, move into `server/openpose` the following directories:
* `models`
* `examples`
* `build`

> **Note**: This directory is necessary for execution of all project.

#### Tests

Auto generated directory that holds all test results, based on [Tester Module](#tester-module) execution.
The directory structure is as follows:
* Video name
	* frames - directory that contains the frames with OpenPose annotations.
	* ground_truth_data - directory that contains csvs based on csv files appears in [Expected Data](#expected_data).
	* test results - directory contains csvs comparing the same colum values from ground truth csv vs. same column values appears in csv generated by OpenPose exectuion (See [Data Extractor Module](#data-extractor-module)).

#### Plug_and_play_functions
Directory for python files to be stored for activating them for swimming error evaluation. Function and file format is identical to the format required here [Evaluator Module](#evaluator-module)

#### Output
This directory keeps all the files generated in the modules described before for all clients and videos uploaded.
The output directory has hierarchy for easy navigation and described by the following path for some specific upload of specific video for specific username:

server/output/< specific username>/< video name > /< upload date >/< upload time>
where < upload date> is in format of DD-MM-YY and < upload time> is in format of HH-MM-SS.

Each specific upload contains the following folders:
* frames - with annotations of OpenPose
* swimfix_annotated_frames- with annotations of keypoints used after filter and interpolation of all keypoints.
* analytical_data - contains csv files generated by [Data Extractor Module](#data-extractor-module).
* figures - contains figures generated by [Visualizer Module](#visualizer-module).

In addition the specific upload folder contains 2 csvs in the level of the directories above. The first one "map.csv" contains mapping between error id and its description. The second on "swimmer_errors.csv" holds the frames that specific swimming error type detected in, for each frame in the uploaded movie.
				 
### Data Base Structure
The server side receives from the client preprocessed videos and saves the produced analytical data to track after the swimmers performance over time. The system saves the following data:
* The videos
* Analytical data produced from the videos and tests- such as csv files and graphs such as body part coordinates as function of time.
*   Edited videos including the Wireframes.
* Information about the user- to associate videos to a specific user.
* Topics and posts of users on the forum.

The system saves this data in a database which contains 5 tables.
> Note: in the "FILES" table we save only the name of the videos, and the videos can be found in the system and not on the database- this is done in order to save the time required in downloading and uploading files from/to a remote database, and to search easily the location of desired file in the server.

**![](https://lh6.googleusercontent.com/Lj8IrR9O43pH0ILHDPYybw8I1ww7U-2dqdMQnGaDMVaoEKsDUhTiIarwDcuxlRIHKcHucaIrIJ5suFjfVdRuRDyTYQCAjnd8KCvA7MY6X8kfYcsUTeGfcSPVV-ies8ykABZGuJjS)**
The sql code to create this database can be found in `server/swimfix_db/swimfix.sql`
For security purposes, we did not upload the python file containing the login credentials to the remote database.<br> An example to the file format can be found at:<br>`server/swimfix_db/swimfix_shadow.py.example`

## Adding Functionality Schema

This is a prototype system for swimming technique fix, and you might want to add new functionality to the system. For this purpose, this guide supplies a simple schema for adding a new functionality supported by both client and server side.<break>
For this guide, we will call our new functionality new_functionality:
>**Assumption**: We create an empty page without any extra-ordinary feature. 
#### From client side:
1. In `client/src/templates`, create `new-functionality.html`.
2. In `index.html`, add to the navigation bar a navigation item with link to the page created in 1. (If this page supposed to be an admin functionality, do the same to  `admin-index.html`).
3. In `client/src/routes.py` create function with the format shown in [Routes File](#routes-file) with respective names to new_functionality.
4. You can help some other function in routes in order to write code sending message to the server, with the following format: < new_request_type > ...

#### From server side:
4. Go to `client_request_parser.py` file and add in the dictionary in the bottom of the page an entry with `'new_request_type': new_functionality`.
5. Create in the same page function named new_functionality that receives all the parameters that the other functions in this page got. You can use those functions to create a code snippet that receives files from client, or sending message or file to the server (if you have to).
6. Create in facade module a function that abstracts the functionality you want to create, and call it from the function you created in section 5.
7. According to your needs, feel free to add new functionalities for other modules existing in the project.

## Assimilation on New Device and Run All Program

We run the system on one computer as a server and with a remote database which its schema defines as follows: [Data Base Structure](#data-base-structure)
For running the system on your own device:
1. Make sure your server computer has the prerequisites for [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose).
2. In `server/main.py` - change HOST to be your server IP address.
3. In `server/swimfix_db/swimfix_shadow.py` change the MYSQL constants according to your database
4. In `client/src/__ init __` - change SERVER_HOST to be your server IP address.
5. Change in `run.py` file in `client/src` line `app.run(host='127.0.0.1',debug=False)`
6. For server side activation: from `server/src`, execute `python main.py`
7. For client side activation: from `client/src`, execute `python run.py`.
<!--stackedit_data:
eyJoaXN0b3J5IjpbMTcyMTg4NDc1OSwxMjExNTU4MTAzLDE3Mj
E4ODQ3NTksMjA0MzI4MTMwNSwtMTMzMzE3NjM3NiwtMTQ4OTky
MjE3OSwxOTczNzc5MDg5LC0xNTY3Njg2MDUyLDE0ODQ0MzY5Mj
gsNjA4MTEzNTcxLDIxMjcyMzE1MTZdfQ==
-->
