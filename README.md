# Rich Man's Deep Learning Camera
Building a Self Contained Deep Learning Camera with the NVIDIA Jetson and Python

![NVIDIA Jetson Deep Learning Camera](https://github.com/burningion/rich-mans-deep-learning-camera/raw/master/images/bird-camera.jpg)

## Installation

You'll need to have OpenCV 3 and Darkflow installed on the NVIDIA Jetson TX1 or TX2. You can use my [fork](https://github.com/burningion/buildOpenCVTX1) of JetsonHacks' build script to get Python 3 support built on the Jetson platform.

Once this is installed, you'll also need to get the Darkflow Tiny Model downloaded and running on the TX1/TX2. With this, you'll just need to install the `imutils` library, and you should be ready to go.

## Architecture

![Deep Learning Camera Architecture](https://github.com/burningion/rich-mans-deep-learning-camera/raw/master/images/jetson.png)

We use an external hard disk, and a USB webcam to take in and store our images. Once we've got a stream of images coming in from the webcam, we run a detection on every other N frames. This allows us to build a pre-buffer, where we can store a tiny movie of the bird before it's detected.

Once it's detected, we create a new thread to continue recording from the webcam, while the original process writes out this pre-buffer to disk.

The inference keeps running until the process itself is killed (usually via CTRL+c).

## Blog Post

The blog post accompanying this repo is at [Make Art with Python](https://www.makeartwithpython.com/blog/rich-mans-deep-learning-camera/). 

## Detected Bird Videos

I've included some example outputs from detected birds in this repo. Good Luck!

![Single Bird](https://github.com/burningion/rich-mans-deep-learning-camera/raw/master/images/bird.gif)
![Bird Duel](https://github.com/burningion/rich-mans-deep-learning-camera/raw/master/images/birdduel.gif)

# Changing What Get's Detected / Recorded, and How Long the Videos Are

Just change the `detectLabel` variable to somethinng out of the Cocos dataset ("person", for example), and then change the `beforeFrames` and `afterFrames`, in order to match your webcam's FPS and the length you'd like. (By default, it's 120, for 4 seconds of 30fps.)
