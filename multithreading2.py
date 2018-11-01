import os, random
from multiprocessing import Process, Queue
from time import sleep
from datetime import datetime
import picamera
import picamera.array
import numpy as np
import cv2
import os,glob

def new_folder(q):
    imagePath = os.path.join('.','Pictures')
    if os.path.exists(imagePath):
        timestr = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        now = datetime.now()
        newDirName = now.strftime('%Y-%m-%d_%H:%M:%S')
        os.mkdir(os.path.join('Pictures',newDirName))
        print('Creating '+newDirName+' folder')
        return new_folder

def start_cam1(q):
    camera = picamera.PiCamera(1)
    camera.sensor_mode = 5
    camera.iso = 100
    sleep(1.2)
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g
    print('Starting capture')
    output = picamera.array.PiBayerArray(camera)
    result = camera.capture(output, 'jpeg', bayer=True)
    debase = (output.demosaic() >> 2).astype(np.uint8)
    q.put(debase)


def start_cam2(q):
    camera = picamera.PiCamera(0)
    camera.sensor_mode = 5
    camera.iso = 100
    sleep(1.2)
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g
    print('Starting capture')
    output = picamera.array.PiBayerArray(camera)
    result = camera.capture(output, 'jpeg', bayer=True)
    debase = (output.demosaic() >> 2).astype(np.uint8)
    q.put(debase)


def save_pic1(q):
    debase=q.get()
    i=0
    b = debase[:,:,0];
    g = debase[:,:,1];
    r = debase[:,:,2];
    for dir in glob.glob('Pictures'):
        if os.path.isdir(dir):
            latest_folder = os.path.getctime(dir)
            folder_time = datetime.fromtimestamp(latest_folder).strftime('%Y-%m-%d_%H:%M:%S')
            newDir= os.path.join(folder_time)
            imageName1 = os.path.join('Pictures',newDir,'IMG_{:04d}_1.tiff'.format(i))
            imageName2 = os.path.join('Pictures',newDir,'IMG_{:04d}_2.tiff'.format(i))
            imageName3 = os.path.join('Pictures',newDir,'IMG_{:04d}_3.tiff'.format(i))
            cv2.imwrite(imageName1,b);
            cv2.imwrite(imageName2,g);
            cv2.imwrite(imageName3,r);
            print('Done!')
            i=i+1
            return save_pic1

def save_pic2(q):
    debase=q.get()
    i=0
    n = debase[:,:,0];
    for dir in glob.glob('Pictures'):
        if os.path.isdir(dir):
            latest_folder = os.path.getctime(dir)
            folder_time = datetime.fromtimestamp(latest_folder).strftime('%Y-%m-%d_%H:%M:%S')
            newDir= os.path.join(folder_time)
            imageName = os.path.join('Pictures',newDir,'IMG_{:04d}_4.tiff'.format(i))
            cv2.imwrite(imageName,n);
            print('Done!')
            i=i+1
            return save_pic2


if __name__ == '__main__':
    q = Queue()
    print('pushing items to queue:')
    a = Process(target=new_folder, args=(q,))
    a.start()
    a.join()
    while True:
        b = Process(target=start_cam1, args=(q,))
        c = Process(target=save_pic1, args=(q,))
        d = Process(target=start_cam2, args=(q,))
        e = Process(target=save_pic2, args=(q,))
        b.start()
        d.start()
        c.start()
        e.start()
        b.join()
        d.join()
        c.join()
        e.join()
