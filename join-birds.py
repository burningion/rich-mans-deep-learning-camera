# This script will convert the captured birds into a video for the day,
# at every end of day. Later, it will also break the images out to
# thumbnails for viewing online.

import glob

numBirdSeqs = len(glob.glob('bird*'))
#print(numBirdSeqs)

with open('image-list.txt', 'w') as imageList:
    for i in range(numBirdSeqs):
        numCurrFiles = len(glob.glob('bird%i/00*.jpg' % (i + 1)))
        for j in range(numCurrFiles):
            imageList.write('file \'bird%i/%05d.jpg\'\n' % (i + 1, j))

# after this join with command: 
# ffmpeg -r 24 -f concat -i image-list.txt -profile:v high -level 4.1 -pix_fmt yuv420p <current_date>.mp4        
# followed by creating thumbnails
# will add this to this script soon


