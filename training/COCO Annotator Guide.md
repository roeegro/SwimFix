# <center> SwimFix<br>COCO Annotator Guide </center>

## Table of Contents
1. [Introduction](#preparing-additional-data-to-train-openpose)
2. [Creating a Category](#creating-a-category)
3. [Adding New Dataset](#adding-new-dataset)
4. [Adding Pictures To The Dataset](#adding-pictures-to-the-dataset)
5. [Annotating Frames](#annotating-frames)
6. [Exporting Products](#exporting-products)

## Preparing Additional Data to Train OpenPose

OpenPose Library is based on deep learning and requires additional data that includes pictures(frames), and in each frames the relevant keypoints are annotated, and the object is identified by segmentation- describing the desired object by its contour.

In this guide we will go through the relevant functionality of the [coco-annotator](https://github.com/jsbroks/coco-annotator) repository which we used in order to annotate our training data in the [COCO](cocodataset.org)  format, so make sure it is up and running before moving on.

## Functionality implemented by the annotator
Note: The following guide describes the functionality needed to annotate keypoints on frames, and doing segmentation on it. The interface contains more functionality which is not relevant to this guide.
### Creating a Category
1.  Choose “Categories” in the main menu which can be found at the top of the page.
2.  A page containing all the categories that were created by you in the past will appear (you can choose category and edit them).
3.  Choose “Create”
4.  In the following page you need to name the new category, and its parent category(optional), and define the keypoints in the category and the relations between them.
### Adding a new dataset   
1.  Choose “Datasets”  in the main menu which can be found at the top of the page.
2.  Choose “Create” option from the page, and enter the new dataset name.  
3.  Go to `SwimmingProject/training/coco-annotator/datasets`, in this directory all the previous datasets can be found. 
5.  Verify that there is a folder with the name you have chosen on step 4.
### Adding pictures To The Dataset
1.  Go to `SwimmingProject/training/coco-annotator/datasets` where all the previous datasets can be found.    
2.  If the desired dataset cannot be found check [Adding a new dataset](#adding-a-new-dataset) above.
3.  Go to the desired dataset directory, in this directory you can create new sub-directories, but we do not recommend doing so.   
4.  Copy into the desired directory the images you want to annotate, and wait a minute.
5.  Go to the annotator web client
6. Choose “Datasets” from the main menu and pick the dataset you want to work with.
7.  Press “Scan” from the left menu to load the pictures to the browser, wait few seconds until the pictures are fully loaded to the page.**![](https://lh4.googleusercontent.com/f2jqXCnJwT2-Czv-Y_dUp6crpBGvKhPYPX3641eLDUrmUJnrqGVk2_k9N6UEADZKvoNydDqfT4ycruWC_H1gRUsPQzaMAnJMnGV4ES8AESBv3UK60K2LbIcMKjl5i7CzaXnknwXb)**
### Annotating Frames
In order to choose the frame you want to annotate follow this steps:

1.  Choose “Datasets” from the main menu.
    
2.  Pick the dataset you want to work with.
    
3.  Pick the frame you want to annotate from the pictures found in the chosen dataset.

Now we will take a look at the annotation interface and describe every feature: 
**![](https://lh5.googleusercontent.com/b9-HUoZ6pItpJqCSNyXC2zotcZWcCrMQcNZrows1VVdTwDKVwlQPggftvITbML2gdUcvJGIckRG2cvuYRwgUHtuqZIvgOTgdbuqtYg36Mu77tsp5KL1guPI3_jbPZmHfcO4eDeEP)**
A:  
Move to the previous frame in the dataset.

B:  
Move to the next frame in the dataset.

C:  
Add entity (in our case: person)  
Note: When you are starting to annotate a new frame- the icon `+` will appear, clicking on it will present the options to initiate a first instance of a category from the categories created in the interface(see “Creating category”).

D:  
Removing the current instance of a chosen categoty. Clicking it will remove all the keypoints and segmentations of this instance.

E:  
List of the keypoints available to annotate.  
Steps of annotation:
-   Choose a keypoint from the list, make sure the chosen keypoint is indicated in green (as can be seen in the picture above).
    
-   Click on the picture in the spot you want to annotate the chosen keypoint.
    
-   The annotation will appear on the frame.
    
-   The browser automatically chooses the next keypoint in the list to annotate, in case you want to choose another keypoint, repeat the first step.
    

Notes:

1.  You can drag existing points on the frame.
    
2.  Every previous annotated point can be removed by pressing the Trash Can icon which appears next to each keypoint previously annotated(see in the image above).

F:  
Classify chosen keypoint from section E by visibility see [keypoints format](http://cocodataset.org/#format-data)
G:  
Pressing this button will cancel the option to annotate the frame and will allow the user to navigate and focus elements in the frame by dragging it with the mouse.

H:  
Pressing this button will allow the user to do segmentation to the desired object in the frame.  

**Steps to segmentate an object in the frame:**

1.  Click on a point on the contour of the desired object.
    
2.  Choose one of the following options:
   
	a.  Hover with the mouse over the frame to make a straight line from the first point, in order to complete the line click once more.
    
	b.  Long press on the mouse button will allow you to define the contour freely by the movement of your mouse.
3.  If you wish to undo the last operation press on the button marked as I.
    
4.  Repeat step 2. until you finish surrounding the object.
    
5.  After finishing surrounding the object, it will be marked in a different color defined by the points you chose on step 2
    
6.  If you wish to cancel segmentation mode press on the button marked as G.
    
7.  You can examine the output, and drag the points around in order to fit best to the contour.**![](https://lh3.googleusercontent.com/12jgqns0EVQFjsrveAhLdXRnW8faBu6ePCiwJhueeCftFHiLhGHXUXLAkk6kihqyepSdVBE65HHTxYYncECRnBF1vttkKfZ0jKzM7HitOQs92t6BxrKfNJn1Zo0PsHaBoxcGXBQ8)**[image for illustration]

I:  
Undo the last operation done by the user.

J:  
Export the current image annotation to a json file- downloaded to the computer from which the operation was called.

K:  
Save changes done on the server.  
Note: The save is done automatically in options A,B but our recommendation is to save every time you finish working on a frame.

L:  
Deleting the current frame from the current dataset.
### Exporting Products
The annotator enables exporting json file the includes in it the details of frames we used, and the rules to make the wireframe from the defined keypoints.  
The format of the json file is described in here: [http://cocodataset.org/#format-data](http://cocodataset.org/#format-data)

To create the file follow this steps:

1.  Press on the “Datasets” button
    
2.  In this page will appear all the previous datasets, press on the icon (:) next to the desired dataset.
    
3.  In the pop-up menu press “Download Coco”, and the download will begin on the client side.**![](https://lh4.googleusercontent.com/9iNRgSxOWHG1GAz06kKHDC80soyh9TQsxoQ2WIUfWk1sPlrLVc2_BaXEzfDo52DCTOL7jXZY1NHQT0jIqxKs72c7T1N-MvyMXfBJmQNDPzk3flM6XWhrFNkNFd-HzMZE02SYnCLI)**
<!--stackedit_data:
eyJoaXN0b3J5IjpbOTE1MTUxMTI2LC05OTA3NDQzNDVdfQ==
-->