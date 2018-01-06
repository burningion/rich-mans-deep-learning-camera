from darkflow.net.build import TFNet
import cv2

from imutils.video import VideoStream
from imutils import resize

import numpy as np

import os
import threading
import time

theCam = VideoStream().start()

options = {"model": "cfg/tiny-yolo-voc.cfg", "load": "bin/tiny-yolo-voc.weights", "threshold": 0.1, "gpu": 0.2}

tfnet = TFNet(options)

# at 30fps, this is 4 seconds
beforeFrames = 120
afterFrames = 120

# skip frames, we'll check n/30 times per second for bird
skipFrames = 10

# label to try detecting
detectLabel = 'bird'

birdDetected = False

birdFrames = 0

birdsSeen = 0

frame = theCam.read()
frame = resize(frame, width=512)


theBuffer = np.zeros((frame.shape[0], frame.shape[1], frame.shape[2], beforeFrames), dtype='uint8')

# prefill buffer with frames
def prefillBuffer():
    for i in range(beforeFrames):
        frame = theCam.read()
        frame = resize(frame, width=512)
        theBuffer[:,:,:,i] = frame
        
prefillBuffer()

currentFrame = 0

def getFramesAfterDetection(fileName, frameBegin, frameLength):
    for i in range(frameLength):
        frame = theCam.read()
        frame = resize(frame, width=512)
        cv2.imwrite('%s%i/%05d.jpg' % (detectLabel, fileName, frameBegin + i), frame)
        # add this sleep as a hack so we don't write the same frame
        # more than once. the tx1 can write faster than 30 fps to disk
        # on my ssd
        time.sleep(.03)

    print('getframes thread finished')

while True:
    # this is the numpy implementation of our circular buffer
    theBuffer = np.roll(theBuffer, -1, axis=3)
    frame = theCam.read()
    frame = resize(frame, width=512)

    theBuffer[:,:,:,-1] = frame

    if not birdDetected:
        currentFrame += 1
        if currentFrame % skipFrames == 0 and currentFrame > 0:
            result = tfnet.return_predict(frame)
            for detection in result:
                if detection['label'] == detectLabel:
                    birdDetected = True
                    birdsSeen += 1
                    print("%s seen!" % detectLabel)
                    if not os.path.exists('%s%i' % (detectLabel, birdsSeen)):
                        os.makedirs('%s%i' % (detectLabel, birdsSeen))

                    # spawn a new thread to start capturing directly from webcam while we save preroll
                    afterT = threading.Thread(target=getFramesAfterDetection, args=(birdsSeen, beforeFrames, afterFrames))
                    afterT.start()

                    # save prebuffer to disk on main thread
                    for i in range(beforeFrames):
                        birdFrames += 1
                        print('writing preframes')
                        cv2.imwrite('%s%i/%05d.jpg' % (detectLabel, birdsSeen, i), theBuffer[:,:,:,i])
                    currentFrame = 0

                    print("preframes %i written" % birdFrames)
                    birdDetected = False
                    birdFrames = 0
                    while afterT.is_alive():
                        time.sleep(0)
                    print("done with thread")
                    prefillBuffer()

                    break


theCam.stop()
