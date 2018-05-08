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
![HD Bird](https://github.com/burningion/rich-mans-deep-learning-camera/raw/master/images/00238.jpg)

# Changing What Gets Detected / Recorded, and How Long the Videos Are

Just change the `detectLabel` variable to somethinng out of the Cocos dataset ("person", for example), and then change the `beforeFrames` and `afterFrames`, in order to match your webcam's FPS and the length you'd like. (By default, it's 120, for 4 seconds of 30fps.)

# Turning Image Sequences into Videos

You can turn any of the images into videos using ffmpeg:

```bash
$ ffmpeg -i %05d.jpg  -profile:v high -level 4.0 -strict -2 out.mp4
```

I also added a script `joinImages.py`, that will create a directory and fill it with all the recorded image sequences. Just run it, and it should grab every bird directory sequentially, and then spit out a new directory with all of the images in order, ready to run the `ffmpeg` command above.

# Getting Images from Videos for Training

Once you've got a day's worth of video, you can quickly run through it for specific events you'd like to add to your dataset.

Save these time points in a file called `timepoints.txt`, with timecodes like the following in hh:mm:ss format:

```
00:00:01
00:04:03
00:06:06
00:17:25
00:18:35
00:18:50
00:20:17
00:23:30
00:34:30
```

Run the `extractTimePoints.py` Python script to extract images from these timepoints using `ffmpeg`:

```
$ python3 extractFromTimePoints.py -f <thedate>.mp4
```

This will create a new directory with images from the timepoints you've selected. You can then label and train these images in something like [labelImg](https://github.com/tzutalin/labelImg) for training.
