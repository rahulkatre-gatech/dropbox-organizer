################################################################################

import os
import sys
import shutil

# Allow for printing in IDLE colors using idle.write().
try:
    idle = sys.stdout.shell
except AttributeError:
    raise RuntimeError('Use IDLE')

# Define a method for displaying list information (length or values).
def display(data, message = '', verbose = False):
    # If verbose logging is enabled (verbose = True) print the entire list.
    # Don't print the message argument.
    if verbose:
        for value in data:
            print(value)
    # Otherwise, print only the size of the dataset, and the message.
    else:
        print(len(data), message)

# Define a method for image/video organization based on their information.
def move(data, file):
    # Define variables for the data in the dataset.
    source = data[file][0]
    outer = data[file][1]
    inner = data[file][2]

    # Create folders if they don't already exist.
    if os.path.exists(outer) and not os.path.exists(inner):
        os.mkdir(inner)
    elif not os.path.exists(outer) and not os.path.exists(inner):
        os.mkdir(outer)
        os.mkdir(inner)

    # Move the image to its proper place.
    destination = inner
    shutil.move(source, destination)

################################################################################

# Change the current working directory to Dropbox > Camera Uploads.
idle.write('Changing working directory...\n', 'STRING')
os.chdir(os.path.join(os.getcwd(), 'Camera Uploads'))
cwd = os.getcwd()
print(cwd)

# Create a list of images/videos in the CWD.
idle.write('\nFinding all unorganized files...\n', 'STRING')
files = []
with os.scandir(cwd) as iterator:
    for entry in iterator:
        if entry.is_file():
            # Create booleans for the different image file endings.
            jpg = entry.name.endswith('jpg')
            png = entry.name.endswith('png')
            mov = entry.name.endswith('mov')

            # Only add the file to the list of files if it is an image.
            if jpg or png or mov:
                files.append(entry.name)

# Stop the script if there are no files that need to be organized.
if not files:
    idle.write('No unorganized files found.', 'COMMENT')
    sys.exit()
else:
    display(files, 'unorganized images/videos found.')

################################################################################

import geopy
import exifread

# Initialize the GeoPy ArcGIS geocoder.
# https://geopy.readthedocs.io/en/stable/#arcgis
idle.write('\nInitializing the ArcGIS geocoder...\n', 'STRING')

# No API key or authentication is necessary for ArcGIS.
maps = geopy.geocoders.ArcGIS()
print('ArcGIS geocoder intialized.')

# Create sets to group based on geotags and store source/destination paths.
idle.write('\nFinding geotagged images...\n', 'STRING')
data = {}
geotagged = []
nongeotagged = []

# Iterate through the files and determine where they should go.
for file in files:
    # Define the source of the file.
    source = os.path.join(cwd, file)

    # Define the name and path of the outer folder (date taken) it should go in.
    date = file[0:10]
    outer = os.path.join(cwd, date)

    # Define a default name for the inner folder (location) it should go in.
    inner = 'Unknown Location'

    # Read the EXIF data of the image.
    image = open(file, 'rb')
    tags = exifread.process_file(image)
    image.close()

    # Filter through the EXIF data to find GPS data.
    gps = [tags[key] for key in tags.keys() if key.startswith('GPS GPSL')]

    # If there is GPS data, change the inner folder name to the street.
    if gps:
        # Convert the coordinates to degrees.
        # compass1 is the compass direction (N or S).
        # degrees1 is in 'degrees, minutes, seconds' (DMS) form.
        # Both are 'ifdtag' objects, so their values must be accessed.
        compass1 = gps[0].values
        degrees1 = gps[1].values

        # Convert DMS into decimal degrees (DD).
        # https://www.latlong.net/degrees-minutes-seconds-to-decimal-degrees

        # Each unit is divided into Ratio objects for hours/minutes/seconds.
        # 'num' is the numerator of the object.
        # 'den' is the denominator of the object.
        # 1 hour/hour, 160 minutes/hour, 3600 seconds/hour.
        latitude = 0.0
        latitude += (degrees1[0].num / degrees1[0].den)/1
        latitude += (degrees1[1].num / degrees1[1].den)/60
        latitude += (degrees1[2].num / degrees1[2].den)/3600

        # Negate the coordinate based on the hemispherical compass value.
        latitude *= -1 if compass1 == 'S' else 1

        # Do the same for longitude.
        compass2 = gps[2].values
        degrees2 = gps[3].values

        longitude = 0.0
        longitude += (degrees2[0].num / degrees2[0].den)/1
        longitude += (degrees2[1].num / degrees2[1].den)/60
        longitude += (degrees2[2].num / degrees2[2].den)/3600
        longitude *= -1 if compass2 == 'W' else 1

        # Reverse-geocode the coordinates and store the name of the street.
        location = maps.reverse((latitude, longitude)).address

        # See if the first character is a number.
        try:
            int(location[0])
        # If it isn't, a value error will be raised.
        # That means there is no street address, just the street name.
        except ValueError:
            # Slice off everything after the road name.
            inner = location[0:location.index(',')]
        # Otherwise. there is a street number in the address.
        else:
            # Slice everything before and after the street.
            inner = location[(location.index(' ') + 1):location.index(',')]

    # If there is no GPS data, add it to the nongeotagged list.
    else:
        nongeotagged.append(file)

    # Define the path of the inner folder the file should go in.
    inner = os.path.join(outer, inner)

    # Store the three paths in a dictionary where the filename is the key.
    data[file] = [source, outer, inner]

# Output the information about those two lists after the loop finishes.
display(geotagged, 'tagged images.')
display(nongeotagged, 'untagged images.')

################################################################################

# Using paths from the dataset, move the files to their places.
idle.write('\nMoving images/videos to assigned folders...\n', 'STRING')
count = 0
for key in data:
    # Call the method that moves the files based on the dictionary.
    move(data, key)
    count += 1
print(count, 'files moved.')
