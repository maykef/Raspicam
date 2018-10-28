from time import sleep
from datetime import datetime
import picamera
import picamera.array
import numpy as np
import cv2
import os,glob

i=0

#imagePath = os.path.join('.','Pictures')

for dir in glob.glob('Pictures'):
  if os.path.isdir(dir):
      latest_folder = os.path.getctime(dir)
      folder_time = datetime.fromtimestamp(latest_folder).strftime('%Y-%m-%d_%H:%M:%S')
      print('Joining '+folder_time+' folder')
      newDirName= os.path.join(folder_time)

#if os.path.exists(imagePath):
#    timestr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#    now = datetime.now()
#    newDirName = now.strftime('%Y-%m-%d %H:%M:%S')
#    os.mkdir(os.path.join('Pictures',newDirName))
#    print('Creating '+newDirName+' folder')

camera0 = picamera.PiCamera(0)
camera1 = picamera.PiCamera(1)

with camera0, camera1:
    camera0.sensor_mode = 6
    camera1.sensor_mode = 6
    #camera0.resolution = (2592, 1944)
    #camera1.resolution = (2592, 1944)
    camera0.iso = 100
    camera1.iso = 100
    sleep(2)
    camera0.shutter_speed = camera0.exposure_speed
    camera1.shutter_speed = camera1.exposure_speed
    camera0.exposure_mode = 'off'
    camera1.exposure_mode = 'off'
    g = camera0.awb_gains
    d = camera1.awb_gains
    camera0.awb_mode = 'off'
    camera1.awb_mode = 'off'
    camera0.awb_gains = g
    camera1.awb_gains = d
    while True:
        print('Capturing images...')
        output0 = picamera.array.PiBayerArray(camera0)
        output1 = picamera.array.PiBayerArray(camera1)
        result = camera0.capture(output0, 'jpeg', bayer=True)
        result1 = camera1.capture(output1, 'jpeg', bayer=True)
        debase = (output0.demosaic() >> 2).astype(np.uint8)
        debase1 = (output1.demosaic() >> 2).astype(np.uint8)
        b = debase[:,:,0];
        g = debase[:,:,1];
        r = debase[:,:,2];
        n = debase1[:,:,0];
        imageName1 = os.path.join('Pictures',newDirName,'IMG_{:04d}_1.tiff'.format(i))
        imageName2 = os.path.join('Pictures',newDirName,'IMG_{:04d}_2.tiff'.format(i))
        imageName3 = os.path.join('Pictures',newDirName,'IMG_{:04d}_3.tiff'.format(i))
        imageName4 = os.path.join('Pictures',newDirName,'IMG_{:04d}_4.tiff'.format(i))
        cv2.imwrite(imageName1,b);
        cv2.imwrite(imageName2,g);
        cv2.imwrite(imageName3,r);
        cv2.imwrite(imageName4,n);
        print('Done!')
        i=i+1
