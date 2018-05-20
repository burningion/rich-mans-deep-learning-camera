# This script will convert the captured birds into a video for the day,
# at every end of day. If it finishes succesfully, it will delete source
# images. Later, it will also break the video out to thumbnails
# for viewing online.

# To install and run at midnight every day, run crontab -e and add the line:
# 0 23 * * * cd /home/nvidia/rich-mans-deep-learning-camera/ && python3 /home/nvidia/rich-mans-deep-learning-camera/join-birds.py
# Replace the above line with your home directory, and where this project is running.

# First, kill the running python3 process to free up memory
# Terrible hack checks for the python3 process using most memory and kills that
# If detector isn't running, kills itself
import subprocess, datetime
import psutil
import glob

import json

try:
    print("Killing existing detector process to free up memory")
    python_processes = [p.info for p in psutil.process_iter(attrs=['pid', 'name', 'memory_info']) if 'python' in p.info['name']]
    if len(python_processes) < 2:
        print("Detector doesn't seem to have been running. Exiting")
        exit()
    command = "kill %i" % python_processes[0]['pid']
    subprocess.check_call(command.split())
except subprocess.CalledProcessError:
    print("Couldn't kill an existing python3 process. Did you run the detector using python3?")
    exit()

# next, create list of detected images for ffmpeg to compress into daily video
# and create an output directory for each portrait and metadat of detection
import glob

today = str(datetime.date.today())
numBirdSeqs = len(glob.glob('bird*'))

create_dir = "mkdir %s" % today
subprocess.check_call(create_dir.split())
print("Creating new directory for day")
with open('image-list.txt', 'w') as imageList:
    for i in range(numBirdSeqs):
        # if this isn't our current date, it's old laying around not deleted
        with open("bird%i/metadata.json" % (i + 1)) as meta:
            metadata = json.load(meta)
            detection_date = datetime.datetime.strptime(metadata['detection_time'], "%c")
            if detection_date.date() != datetime.datetime.now().date():
                print("Skipping folder bird%i as it's older than today" % (i + 1))
                break
        numCurrFiles = len(glob.glob('bird%i/00*.jpg' % (i + 1)))
        for j in range(numCurrFiles):
            imageList.write('file \'bird%i/%05d.jpg\'\n' % (i + 1, j))
        copy_metadata = "cp bird%i/metadata.json ./%s/" % (i + 1, today)
        subprocess.check_call(copy_metadata.split())
        copy_portrait = "cp bird%i/portrait.jpg ./%s/portrait%05d.jpg" % (i + 1, today, i + 1)
        subprocess.check_call(copy_portrait.split())

# create video file with current date with ffmpeg
print("Running ffmpeg, this could take a while")
try:
    command = "ffmpeg -r 24 -f concat -i image-list.txt -profile:v high -level 4.1 -pix_fmt yuv420p %s.mp4" % today
    subprocess.check_call(command.split())
except subprocess.CalledProcessError:
    print("Couldn't create the video summary of the day.")
    exit()

# delete the original bird images
print("ffmpeg ran successfully, deleting original images")
try:
    command = "rm -rf bird*"
    subprocess.check_call(command.split())
except subprocess.CalledProcessError:
    print("Couldn't delete old detected bird images.")
    exit()

# and restart the python detection process once more
print("Restarting python detection process")
command = "nohup python3 /home/nvidia/rich-mans-deep-learning-camera/richierich.py -u http://10.0.0.3:5000/image.jpg"
subprocess.call(command.split())

