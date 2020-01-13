# dropbox-organizer

A script I wrote in 2018 for the City of Stamford Health Department to automatically organize pictures taken by health inspectors. The iPads used by the inspectors capture images and location data, and automatically upload each image file to a shared Dropbox. However, since the images are not organized, this script will organize them into a hierarchy of folders. Organizing thousands of images manually would be too great of a task, whereas this script can be run multiple times, organizing unfiled images each time it is run. 

There are two levels of folders the script organizes images into. The folders in the upper level are named after the day the pictures in them were taken on. The folders in the lower level are named after the street (obtained through reverse-geocoding) the pictures were taken at. This is useful to the inspectors, who also write reports, as it is easy for them to find their images based on where it was taken. 
