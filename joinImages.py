import glob
import shutil

# this joins each of the individual detections into one long image sequence
for filename in glob.glob('bird*'):
    print(filename)
    for i in range(240):
        shutil.copyfile(filename + ('/%05d.jpg' % i), ('outvideo/%05d.jpg'  % ((int(filename[4:]) - 1) * 240 + i)))
