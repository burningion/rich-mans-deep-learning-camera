import os
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--filename', help="Input video filename", required=True)
parsed = parser.parse_args()

counter = 0

video_date = parsed.filename.split('.')[0]
if not os.path.exists(video_date):
    os.makedirs(video_date)

with open('timepoints.txt') as timepoints:
    for timepoint in timepoints:
        counter += 1
        print("Extracting timepoint %s" % timepoint)
        command = "ffmpeg -ss %s -i %s -vframes: 40 -q:v 2 -r 2 %s/%i-%%05d.png" % (timepoint, parsed.filename, video_date, counter)
        subprocess.check_call(command.split())
