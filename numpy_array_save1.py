import time
import picamera
import picamera.array
import numpy as np
import cv2

with picamera.PiCamera(1) as camera:
    with picamera.array.PiBayerArray(camera) as stream:
        camera.capture(stream, 'jpeg', bayer=True)
        #output = (stream.demosaic() >> 2).astype(np.uint8)
        output = (output.array.astype(np.uint8))
        b = output[:,:,0]
        g = output[:,:,1]
        r = output[:,:,2]
        cv2.imwrite('image_1.tiff',b)
        cv2.imwrite('image_2.tiff',g)
        cv2.imwrite('image_3.tiff',r)
