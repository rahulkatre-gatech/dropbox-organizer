# Dropbox Organizer
**File:** `Organize.py` or `Organize CMD.py`

**Author:** Rahul Katre

---

### Section 1

    import os
    import sys
    import time
    import geopy
    import shutil
    import exifread
    
Python packages that will be used by the program. `os`, `sys`, `time`, and `shutil` are all built in, so there is no need to use `pip` to install them. `geopy` and `exifread` are not part of Python, so following commands were used to install them. 

    pip install geopy
    pip install exifread

Ensure that `pip` is installed already and that Python has been added to PATH.

&nbsp;

### Section 2

	from colorama import init
	from termcolor import colored

Two packages that are only for colored outputs to the command line (not IDLE). They were installed through `pip` using the following commands.

	pip install colorama
    pip install termcolor
    
Once again, ensure that `pip` is installed already and that Python has been added to PATH.

&nbsp;

### Section 3

	def display(data, message, verbose = False):
    	if verbose:
        	[print(value) for value in data]
	    else:
    	    print(len(data), message)
            
Method that outputs information about lists, and can be toggled between verbose and non-verbose through the use of the `verbose` argument, whose default value is or non-verbose, or `False`. Verbose output displays every item in the list and ignores the message argument. Non-verbose output  displays the length of the list and the message argument, which should be used to describe the information in the list.

&nbsp;

### Section 4

	def decimal(compass, degree):
    	value = 0.0
    	value += (degree[0].num / degree[0].den)/1
    	value += (degree[1].num / degree[1].den)/60
	    value += (degree[2].num / degree[2].den)/3600

	    return value if compass == 'N' or compass == 'E' else value * -1
        
Method that converts the coordinates in the geotags from degrees, minutes, seconds (DMS) to decimals (DD). `degree` is an array of three `Ratio` objects, and each entry in the array represents either degrees, minutes, or seconds in the DMS format. As they are `Ratio` objects, their numerators and denominators must be accessed first so that the numerator can be divided by the denominator to get a `float`. 

Degrees can be thought of as hours, and since there are 60 minutes in an hour and 3600 seconds in an hour, to convert to DD, everything must be in hours. So the "minutes" decimal must be divided by 60, and the "seconds" decimal must be divided by 3600. The sum of the three values after the math will be the DD coordinates. 

However, the DD coordinates still need to be negated based on the hemisphere (N/S or E/W). The DD coordinates are negative in the southern or western hemispheres, so an inline-if-statement handles these cases when returning the DD coordinate.

&nbsp;

### Section 5

	def convert(compass1, compass2, degrees1, degrees2):
    	latitude = decimal(compass1, degrees1)
	    longitude = decimal(compass2, degrees2)

    	return (latitude, longitude)
        
Method that uses the `decimal()` method to convert the values of the four EXIF tags of the image that pertain to latitude and longitude from DMS into DD, and returns a tuple that will be used to reverse-geocode the coordinates.

&nbsp;

### Section 6

	def move(data, file):
    	source = data[file][0]
	    outer = data[file][1]
	    inner = data[file][2]

	    if os.path.exists(outer) and not os.path.exists(inner):
	        os.mkdir(inner)
	    elif not os.path.exists(outer) and not os.path.exists(inner):
	        os.mkdir(outer)
	        os.mkdir(inner)

    	destination = inner
	    shutil.move(source, destination)
        
Method that accesses a dictionary that contains the following information:

	{ file_name : [source_path, date_folder, location_folder] }
   
The dictionary is added to later in the program just after where reverse-geocoding takes place. 	`source_path` is the location of the file, which should be in Camera Uploads. `date_folder` is the path of the folder named after the date the file was created (picture/video was taken), and `location_folder` is the path of the folder named after the street the picture was taken on. 

It is possible that `date_folder` and also `location_folder` already exist. It should be noted that `location_folder` will always exist inside of `date_folder`, which is why the chained `os.mkdir()` commands will work. The method first stores the value list under the `file` key in the `data` dictionary in its own local variables. Then, it checks to see if the directories that are being pointed to already exist; if they don't it will create them. At the end, the file gets moved from its `source` to its `destination`.

&nbsp;

### Section 7

	init()
	print(colored('Starting program...', 'cyan'))
    
Initialize the `colorama` package to enable colored command line printing, and then print a message to show the start of the program.

&nbsp;

### Section 8

	print(colored('\n' + 'Changing working directory...', 'green'))
	os.chdir(os.path.join(os.getcwd(), 'Camera Uploads'))
	cwd = os.getcwd()
	print(cwd + '\n')
    
Change the working directory of the program from the location of the program (`Dropbox`) to the location of the unorganized media files (`Dropbox/Camera Uploads`).

&nbsp;

### Section 9

	print(colored('Initializing the ArcGIS geocoder...', 'green'))
	maps = geopy.geocoders.ArcGIS()
	print('ArcGIS geocoder intialized.' + '\n')

Initialize the ArcGIS geocoder. No API key is required for initialization, so no arguments are necessary. Documentation for the initializing thr geocoders provided by `geopy` (which includes ArcGIS) can be found at [https://geopy.readthedocs.io/en/stable](). 

&nbsp;

### Section 10

	print(colored('Finding all unorganized files...', 'green'))
	with os.scandir(cwd) as iterable:
    	files = []
	    for entry in iterable:
	        if entry.is_file():
	            jpg = entry.name.endswith('jpg')
	            png = entry.name.endswith('png')
	            mov = entry.name.endswith('mov')
	
	            if jpg or png or mov:
	                files.append(entry.name)

Generate a list of everything in `Dropbox/Camera Uploads` by using the `os.scandir()` method, which returns an iterable. Iterate through the iterable to find entries that are files. If the file is an image (`.jpg` or `.png`) or a video (`.mov`), add it to `files`, a list of files that need to be organized.

&nbsp;

### Section 11
	
    if not files:
    	print(colored('No unorganized files found.', 'red'))
        sys.exit()
	else:
    	display(files, 'unorganized images/videos found.')

If there are no files that are unorganized, then `files` will be empty. If so, the program can be terminated. Otherwise, the program will continue. The other lines in this section are only for outputting to the command line.

&nbsp;

### Section 12

	print(colored('\n' + 'Finding locations of images...', 'green'))
	data = {}
	geotagged = []
	nongeotagged = []

Define a dictionary and two lists to keep track of the files. The two lists are not necessary for the program, but are there for output and debugging purposes. 

&nbsp;

### Section 13

	for file in files:
	    date = file[:10]
    	source = os.path.join(cwd, file)
	    outer = os.path.join(cwd, date)
	    inner = 'Unknown Location'

In the first part of the main loop, define a variable `date` for the date the picture was taken (which is the first ten characters of the file name). Then, define the source path, which should be `Dropbox/Camera Uploads/[file]`. `outer` represents the date folder, so the `date` variable will be used here to point to a folder for the date the file was created (which is the date the picture or video was taken). 

Since a location is not known yet, the default value for the inner folder, whose name is stored in `inner`, will be "Unknown Location". Its path will not be generated now as it is possible that this value could change. 

&nbsp;

### Section 14

	    with open(file, 'rb') as image:
    	    tags = exifread.process_file(image)
        	gps = [tags[key] for key in tags.keys() if key.startswith('GPS GPSL')]

Open the file so that its EXIF data can be read. `exifread` is used here to store the EXIF tags into the `tags` dictionary. `tags` is then filtered for its GPS-coordinate-related tags, and the values of those keys are stored in the `gps` list.
  
&nbsp;

### Section 15

	    if gps:        
    	    compass1 = gps[0].values
        	compass2 = gps[2].values
	
    	    degrees1 = gps[1].values
    	    degrees2 = gps[3].values
	
        	coordinates = convert(compass1, compass2, degrees1, degrees2)
	        time.sleep(0.5)
    	    location = maps.reverse(coordinates).address
	        geotagged.append(file)

    	    try:
	            int(location[0])
    	    except ValueError:
        	    inner = location[0:location.index(',')]
    	    else:
	            inner = location[(location.index(' ') + 1):location.index(',')]
	    else:
    	    nongeotagged.append(file)

If there are values in `gps`, then a location for the image can be found. Since the values in `gps` are `IFDTag` objects, their raw values must be accessed through `.values`. The first and third values in `gps` represent the hemisphere (N/S, E/W), while the second and fourth values represent the coordinate in DMS form. 

These four values are passed to the `convert()` method, where `decimal()` is called on the compass/degree pairs to return a coordinate in DD form. In `convert()`, the coordinate pairs are returned as a latitude/longitude tuple, which is stored in `coordinates`. With the coordinates in DD form, the ArcGIS geocoder can be used to reverse-geocode the coordinates so that the street address of the coordinates can be obtained. Now that an address has been obtained, the file can be noted down in the `geotagged` list.

In order to filter out unnecessary parts of the address, since only the road name is needed, check to see if there are numbers at the beginning of the address, as ArcGIS can sometimes output addresses that don't have numbers at the beginning. Attempting to convert the first character to a number and then checking if an error occurred will verify this. 

Based on the result, slice either the number and everything after the road name if there is a number, or just everything after the road name if there is the number. Store this sliced string in `inner`, as the name of the inner folder will be the street name.

If there were no GPS values, no reverse-geocoding is necessary. The file can then be noted down in the `nongeotagged` list. No changes to `inner` will take place as the the file will be stored in "Unknown Location", which is the default value of `inner`.

&nbsp;

### Section 16

	    inner = os.path.join(outer, inner)
    	data[file] = [source, outer, inner]

Now that all changes (if any) have been made to `inner`, the path of the inner folder can be generated by joining `inner` with the path of the outer folder, stored in `outer`. Add a list containing the source path of the file, the outer folder that the file should go in, and the inner folder (inside the outer folder) that the file should go in, to the dictionary under a key that is the file's name. 

&nbsp;

### Section 17

	print(colored('Counting geotagged images...', 'green'))
	display(geotagged, 'geotagged images.')

	print(colored('\n' + 'Counting nongeotagged images...', 'green'))
	display(nongeotagged, 'nongeotagged images.')

Output statistics about the number of geotagged and nongeotagged images that will be organized. If verbose output is enabled, output the name of every file in those categories.

&nbsp;

### Section 18

	count = 0
	print(colored('\n' + 'Moving images/videos to assigned folders...', 'green'))
	for key in data:
    	move(data, key)
	    count += 1
	print(count, 'files moved.')
    
With a dictionary of instructions having been genrated, the `move()` method can be called on every entry in the dictionary by using a for-in loop. Keep track of the number of files moved through a counting variable. 

&nbsp;
