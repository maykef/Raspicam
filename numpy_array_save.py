import time
import picamera
import picamera.array
import numpy as np
import cv2

with picamera.PiCamera(1) as camera:
    with picamera.array.PiBayerArray(camera) as stream:
        camera.capture(stream, 'jpeg', bayer=True)
        output = (stream.demosaic() >> 2).astype(np.uint8)
        n = output[:,:,0]
        cv2.imwrite('image_4.tiff',n)
