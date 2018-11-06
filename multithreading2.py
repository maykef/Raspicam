from multiprocessing import Process, Pipe
from time import sleep
from datetime import datetime
import picamera
import picamera.array
import numpy as np
import cv2
import os,glob


def new_folder():
    imagePath = os.path.join('.','Pictures')
    if os.path.exists(imagePath):
        timestr = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        now = datetime.now()
        newDirName = now.strftime('%Y-%m-%d_%H:%M:%S')
        os.mkdir(os.path.join('Pictures',newDirName))
        print('Creating '+newDirName+' folder')
        return new_folder

def start_cam1(conn):
    camera = picamera.PiCamera(1)
    camera.sensor_mode = 5
    camera.iso = 100
    sleep(0.6)
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g
    camera.exif_tags['IFD0.Copyright'] = 'Copyright (c) 2013 Agrosight Ltd'
    camera.exif_tags['EXIF.ImageUniqueID'] = '70995432222RE'
    print('Starting capture')
    output = picamera.array.PiBayerArray(camera)
    result = camera.capture(output, 'jpeg', bayer=True)
    #debase = (output.demosaic() >> 2).astype(np.uint8)
    debase = ((output.array >>2).astype(np.uint8))
    conn.send(debase)


def start_cam2(conn):
    camera = picamera.PiCamera(0)
    camera.sensor_mode = 5
    camera.iso = 100
    sleep(0.6)
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g
    camera.exif_tags['IFD0.Copyright'] = 'Copyright (c) 2013 Agrosight Ltd'
    camera.exif_tags['EXIF.ImageUniqueID'] = '70995432222RE'
    print('Starting capture')
    output = picamera.array.PiBayerArray(camera)
    result = camera.capture(output, 'jpeg', bayer=True)
    #debase1 = (output.demosaic() >> 2).astype(np.uint8)
    debase = ((output.array >>2).astype(np.uint8))
    conn.send(debase)


def save_pic1(conn):
    dt = datetime.now().strftime("%M_%S")
    debase=conn.recv()
    b = debase[:,:,0];
    g = debase[:,:,1];
    r = debase[:,:,2];
    for dir in glob.glob('Pictures'):
        if os.path.isdir(dir):
            latest_folder = os.path.getctime(dir)
            folder_time = datetime.fromtimestamp(latest_folder).strftime('%Y-%m-%d_%H:%M:%S')
            newDir= os.path.join(folder_time)
            imageName1 = os.path.join('Pictures',newDir,'IMG_'+dt+'_1''.tiff')
            imageName2 = os.path.join('Pictures',newDir,'IMG_'+dt+'_2''.tiff')
            imageName3 = os.path.join('Pictures',newDir,'IMG_'+dt+'_3''.tiff')
            cv2.imwrite(imageName1,b);
            cv2.imwrite(imageName2,g);
            cv2.imwrite(imageName3,r);
            print('Done!')
            return save_pic1

def save_pic2(conn):
    dt = datetime.now().strftime("%M_%S")
    debase1=conn.recv()
    n = debase1[:,:,0];
    for dir in glob.glob('Pictures'):
        if os.path.isdir(dir):
            latest_folder = os.path.getctime(dir)
            folder_time = datetime.fromtimestamp(latest_folder).strftime('%Y-%m-%d_%H:%M:%S')
            newDir= os.path.join(folder_time)
            imageName = os.path.join('Pictures',newDir,'IMG_'+dt+'_4''.tiff')
            cv2.imwrite(imageName,n);
            print('Done!')
            return save_pic2


if __name__ == '__main__':
    new_folder()
    start_conn, save_conn = Pipe()
    start1_conn, save2_conn = Pipe()
    while True:
        start = Process(target=start_cam1, args=(start_conn,))
        save = Process(target=save_pic1, args=(save_conn,))
        start1 = Process(target=start_cam2, args=(start1_conn,))
        save2 = Process(target=save_pic2, args=(save2_conn,))
        start.start()
        save.start()
        start1.start()
        save2.start()
        start.join()
        save.join()
        start1.join()
        save2.join()
