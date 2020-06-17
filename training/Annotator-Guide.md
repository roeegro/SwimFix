# <center> SwimFix<br>COCO Annotator Guide </center>

## Table of Contents
1. [Introduction](#preparing-additional-data-to-train-openpose)
1. [Creating VPN Connection To The Annotator Server](#creating-vpn-connection-to-the-annotator-server)
4. [Creating Category](#creating-category)
5. [Adding New Dataset](#adding-new-dataset)
6. [Adding Pictures To The Dataset](#adding-pictures-to-the-dataset)
7. [Annotating Frames](#annotating-frames)
8. [Exporting Products](#exporting-products)

## Preparing Additional Data to Train OpenPose

OpenPose Library is based on deep learning and requires additional data that includes pictures(frames), and in each frames the relevant keypoints are annotated, and the object is identified by segmentation- describing the desired object by its contour.

In order to prepare more data to train the OpenPose library follow this steps:
### Creating VPN connection to the annotator server
1.  Creating vpn connection in the following link:  
    [https://in.bgu.ac.il/computing/Pages/vpn-service.aspx](https://in.bgu.ac.il/computing/Pages/vpn-service.aspx)
    
2.  Search “vpn settings” in the operating system search tool.**![](https://lh3.googleusercontent.com/9wri_Zh5DUUxo8bRgAjJ9goRYQL7KADM-73BZFlInrr0zhcdvv0Awm39kPtRbW23-YDsIw1l2iM4n13HuWSKwCfOjMkKnOYnY8LGPGKWC14jFl-K4jiVcgkgL-sUJ7cv7vhcfWhE)**
3. Press “Connect” to the vpn connection from step 1.**![](https://lh3.googleusercontent.com/zVuuNZrnO9oGSb9aDZIXmVW_r1wccTWwN9fSZAfieN3K3Qogxabi5DsVB96oN39dyxWtzc6O_4odMPlP6N7oUjzrDM6rHYHmMECDODLffnzf9IupMVQ1hO6CvES5cDQzS7y0vr8s)**
4. Enter your credentials in the same format as in the picture, the password will be given by the RSA Authenticator application from step 1.
<break>**![](https://lh6.googleusercontent.com/IzpMqrbDQcqtFiME5DpVJEj7p5Tc6S8lfoSuwOrqVafcnC7CpsGJeNoG7c5VOCXCfRoyHJVEivUQXXo6cXgqLU97OPipUTkqjb75oXVWYUoa92D80uOEzKXfjZqE3ODbdtTY3cQ-)**
5. In order to connect to the server, Search “remote desktop connection” in the operating system search tool.**![](https://lh6.googleusercontent.com/Y2dMG-yZ0p2BYS3OF9hVW1kRqwaNb3B6ui_UAZp7aV1G3pvqGstw-4vA0ER44Ke-Oo2WWOAcs6Ehijdlxr-JjU5Xj_TG5UScDEcVMCfja36HveO506knonAvIYPkqVRhHpj4z_Vo)**
6. Enter the credentials in the same format as in the picture.<break>
**![](https://lh5.googleusercontent.com/Sc6eyIUKbjO7-lhT5aq1pb3lWttg1Ar1FU5x-tdLpEgNOw2wIfw3RYo6fSaO_P_cn8AqTWhBwW8qsa0dqADJ7f7Ozsi_4_bhkaZsNMozURSKpp0Re70vdaPDiQ_FheZ2IGEpGUZj)**
7. To connect to the server you need to enter your username and password from BGU.
	* You need permission to access the computer. Email address to ask authorization: rriemer@bgu.ac.il.

8.	Now we will activate the server. On the start menu press the `^` icon, and search the Docker icon.**![](https://lh6.googleusercontent.com/hIjwMZMzjuxYeyv-UoERniB5abTCCB39ijXpd4Cv28qD-lmVKQb097-8KokHnehEqPHE3n3ujMTEMhTnVrPdiFB-O1F0xJT2qQDMznLdELLrpYc4rWKHkWzbhNUYKaZNdc3ocn2u)**
9.  Right click the docker icon, choose Start Docker and wait until “Docker is running” notification.
    
10.  Click again on the Docker icon and choose “Dashboard”.
    
11.  Verify “annotator_webclient” is activated (indicated in green), if not, press on the Play button as described in the picture.**![](https://lh6.googleusercontent.com/Pieffo-DUeBVRRZzoRNeLTR2I5BfU0xscoiPmCHJpPoqW9IHds-g393WTBIfyIhxDbmvCCCTzYnWNzwYxW4MsCBJByAj2MeZzBwsn7_4T3OZJjxu5bAMIOqPyubn7XFQh9XWFodf)**
12.   Enter the browser and enter the URL “localhost:5000” to verify the connection succeed
    

-   If it succeed a login panel will appear, you can create username and password and enter the interface.
    
-   If the connection failed, wait 30 seconds, and do step 8 again, but try choosing the Restart option. 

**Note:** After step 9, when the server is up, you can keep the remote desktop working, go back to the personal computer to use the annotator tool (next page).  
Work from the personal computer can be accessed by entering the browser url: `132.72.96.31:5000`

## Functionality implemented by the annotator server
Note: The following guide describes the functionality needed to annotate keypoints on frames, and doing segmentation on it. The interface contains more functionality which is not relevant to this guide.
### Creating Category
1.  Choose “Categories” in the main menu which can be found at the top of the page.
    
2.  A page containing all the categories that were created by you in the past will appear (you can choose category and edit them).
    
3.  Choose “Create”
    
4.  In the following page you need to name the new category, and its parent category(optional), and define the keypoints in the category and the relations between them.
### Adding new dataset
1.  Login to the remote desktop (see “Creating VPN connection to the annotator server”)
    
2.  Enter the url in the browser (from the remote desktop) “localhost:5000”, and enter with your user.
    
3.  Choose “Datasets” from the main menu.
    
4.  Choose “Create” option from the page, and enter the new dataset name.
    
5.  Enter the directory `D:/SwimmingProject/Coco-annotator`, in this directory the server’s code is found.
    
6.  Enter the “datasets” directory, in this directory all the previous datasets can be found.
    
7.  Verify that there is a folder with the name you have chosen on step 4.
### Adding pictures To The Dataset
1.  Login to the remote desktop (see “Creating VPN connection to the annotator server”)
    
2.  Enter the directory `D:/SwimmingProject/Coco-annotator` in this directory the server’s code is found.
    
3.  Enter the “datasets” directory, in this directory all the previous datasets can be found.
    
4.  If the desired dataset cannot be found see “Adding new dataset” in this guide.
    
5.  Enter the desired dataset directory, in this directory you can create new sub-directories, we do not recommend doing so.
    
6.  Copy into the desired directory the frames you want to annotate, and wait a minute.
    
7.  Enter the url in the browser (from the remote desktop) “localhost:5000”, and enter with your user.
    
8.  Choose “Datasets” from the main menu and pick the dataset you want to work with.
    
9.  Press “Scan” from the left menu to load the pictures to the browser, wait few seconds until the pictures are fully loaded to the page.**![](https://lh4.googleusercontent.com/f2jqXCnJwT2-Czv-Y_dUp6crpBGvKhPYPX3641eLDUrmUJnrqGVk2_k9N6UEADZKvoNydDqfT4ycruWC_H1gRUsPQzaMAnJMnGV4ES8AESBv3UK60K2LbIcMKjl5i7CzaXnknwXb)**
10. After completing the instructions above successfully, you can access to the desired dataset from the browser of any computer that can access to the remote desktop.
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
Classify chosen keypoint from section E by visibility (see keypoints format :[http://cocodataset.org/#format-data](http://cocodataset.org/#format-data))

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