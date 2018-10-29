from time import sleep
from datetime import datetime
import picamera
import picamera.array
import numpy as np
import cv2
import os,glob

i=0

for dir in glob.glob('Pictures'):
  if os.path.isdir(dir):
      latest_folder = os.path.getctime(dir)
      folder_time = datetime.fromtimestamp(latest_folder).strftime('%Y-%m-%d_%H:%M:%S')
      print('Joining '+folder_time+' folder')
      newDirName= os.path.join(folder_time)

camera = picamera.PiCamera(1)

with camera:
    camera.sensor_mode = 5
    camera.iso = 100
    sleep(2)
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g
    while True:
        print('Capturing images...')
        output = picamera.array.PiBayerArray(camera)
        result = camera.capture(output, 'jpeg', bayer=True)
        debase = (output.array.astype(np.uint8))
        n = debase[:,:,0];
        imageName = os.path.join('Pictures',newDirName,'IMG_{:04d}_4.tiff'.format(i))
        cv2.imwrite(imageName,n);
        print('Done!')
        sleep(2)
        i=i+1
