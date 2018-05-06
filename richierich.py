from darkflow.net.build import TFNet
import cv2

from imutils.video import VideoStream
from imutils import resize

import numpy as np

import os
import threading
import time

import subprocess
import json

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-u', "--url", type=str, help="Url to hit to grab another image perspective")
parsed = parser.parse_args()

vs = VideoStream(resolution=(1280,720), framerate=30)
vs.stream.stream.set(3, 1280)
vs.stream.stream.set(4, 720)

theCam = vs.start()

options = {"model": "cfg/tiny-yolo-voc.cfg", "load": "bin/tiny-yolo-voc.weights", "threshold": 0.1, "gpu": 0.2}

tfnet = TFNet(options)

beforeFrames = 30
afterFrames = 240

# skip frames, we'll check n/30 times per second for bird
skipFrames = 10

# label to try detecting
detectLabel = "bird"

birdDetected = False

birdFrames = 0

birdsSeen = 0

frame = theCam.read()
#frame = resize(frame, width=512)


theBuffer = np.zeros((frame.shape[0], frame.shape[1], frame.shape[2], beforeFrames), dtype='uint8')

# prefill buffer with frames
def prefillBuffer():
    for i in range(beforeFrames):
        frame = theCam.read()
        #frame = resize(frame, width=512)
        theBuffer[:,:,:,i] = frame

def getHighRes(detectLabel, birdsSeen, url):
    # gets a high res image from raspberry pi camera v2 server
    # https://github.com/burningion/poor-mans-deep-learning-camera
    # (optional!)
    return subprocess.Popen(['wget', '-O', '%s%i/portrait.jpg' % (detectLabel, birdsSeen), url])


prefillBuffer()

currentFrame = 0

def getFramesAfterDetection(fileName, frameBegin, frameLength):
    for i in range(frameLength):
        frame = theCam.read()
        #frame = resize(frame, width=512)
        cv2.imwrite('%s%i/%05d.jpg' % (detectLabel, fileName, frameBegin + i), frame)
        # add this sleep as a hack so we don't write the same frame
        # more than once. the tx1 can write faster than 30 fps to disk
        # on my ssd
        time.sleep(.01)

    print('getframes thread finished')

while True:
    # this is the numpy implementation of our circular buffer
    theBuffer = np.roll(theBuffer, -1, axis=3)
    frame = theCam.read()
    #frame = resize(frame, width=512)

    theBuffer[:,:,:,-1] = frame

    if not birdDetected:
        currentFrame += 1
        if currentFrame % skipFrames == 0 and currentFrame > 0:
            frame = resize(frame, width=512)
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
                    if parsed.url:
                        getHighRes(detectLabel, birdsSeen, parsed.url)
                    while afterT.is_alive():
                        time.sleep(0)
                    print("done with thread")
                    with open('%s%i/metadata.json' % (detectLabel, birdsSeen), 'w') as metadata:
                        det = {'detections': result, 'detection_time': time.ctime()}
                        for detection in det['detections']:
                            detection['confidence'] = float(detection['confidence'])
                        json.dump(det, metadata)
                    prefillBuffer()

                    break


theCam.stop()
