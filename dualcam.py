import RPi.GPIO as GPIO
import glob
import os
from datetime import datetime
from multiprocessing import Process, Pipe
import cv2
import numpy as np
import picamera.array
import picamera

GPIO.setmode(GPIO.BCM)
GPIO.setup(13,GPIO.IN)


def new_folder():
    """Creates a new folder each time the script runs"""
    imagepath = os.path.join('.', 'Pictures')
    if os.path.exists(imagepath):
        datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        now = datetime.now()
        newdirname = now.strftime('%Y-%m-%d_%H:%M:%S')
        os.mkdir(os.path.join('Pictures', newdirname))
        print('Creating '+newdirname+' folder')
        return new_folder

def start_cam1(conn):
    """Starts camera cs 0 in the Compute Module"""
    camera = picamera.PiCamera(0)
    """Let's capture images with equal parameters"""
    camera.sensor_mode = 1
    camera.iso = 100
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g
    print('Starting capture')
    """Capture raw Bayer data"""
    output = picamera.array.PiBayerArray(camera)
    camera.capture(output, 'jpeg', bayer=True)
    """Let's save the raw Bayer pattern into an array,\
    shift pixels by 2-bits, and save image as uint8"""
    debase = ((output.array >>2).astype(np.uint8))
    """Now let's save the array and share it with our \
    process save_pic1"""
    conn.send(debase)


def start_cam2(conn):
    """Starts camera cs 1 in the Compute Module"""
    camera = picamera.PiCamera(1)
    """Let's capture images with equal parameters"""
    camera.sensor_mode = 1
    camera.iso = 100
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g
    print('Starting capture')
    """Capture raw Bayer data"""
    output = picamera.array.PiBayerArray(camera)
    camera.capture(output, 'jpeg', bayer=True)
    """Let's save the raw Bayer pattern into an array,\
    shift pixels by 2-bits, and save image as uint8"""
    debase = ((output.array >>2).astype(np.uint8))
    """Now let's save the array and share it with our \
    process save_pic2"""
    conn.send(debase)


def save_pic1(conn):
    """Let's call datetime so our image name includes it"""
    dt = datetime.now().strftime("%M_%S.%f")[:-3]
    """Receive the array from start_cam1"""
    debase=conn.recv()
    """Deconstruct the array into three (red, green and blue) channels"""
    r = debase[:,:,0]
    g = debase[:,:,1]
    b = debase[:,:,2]
    """Let's join the folder created by new_folder"""
    for dir in glob.glob('Pictures'):
        if os.path.isdir(dir):
            latest_folder = os.path.getctime(dir)
            folder_time = datetime.fromtimestamp(latest_folder).strftime('%Y-%m-%d_%H:%M:%S')
            newdir = os.path.join(folder_time)
            """Prepare the new name for each image"""
            imagename1 = os.path.join('Pictures', newdir, 'IMG_'+dt+'_1''.tiff')
            imagename2 = os.path.join('Pictures', newdir, 'IMG_'+dt+'_2''.tiff')
            imagename3 = os.path.join('Pictures', newdir, 'IMG_'+dt+'_3''.tiff')
            """Now demosaic the images using opencv; bear in mind that \
            our Bayer pattern is RGGB, so the second row and columns \
            are GR"""
            r = cv2.cvtColor(r, cv2.COLOR_BayerGR2RGB)
            g = cv2.cvtColor(g, cv2.COLOR_BayerGR2RGB)
            b = cv2.cvtColor(b, cv2.COLOR_BayerGR2RGB)
            """BayerGR2RGB will create an image with three channels, \
            so we need to transform them into single channel images \
            again"""
            cv2.imwrite(imagename1, r[:,:,0])
            cv2.imwrite(imagename2, g[:,:,1])
            cv2.imwrite(imagename3, b[:,:,2])
            print('Done!')
            return save_pic1

def save_pic2(conn):
    """Let's call datetime so our image name includes it"""
    dt = datetime.now().strftime("%M_%S.%f")[:-3]
    """Receive the array from start_cam1"""
    debase1=conn.recv()
    """Deconstruct the array into one (NIR) channel"""
    n = debase1[:, :, 0]
    """Let's join the folder created by new_folder"""
    for dir in glob.glob('Pictures'):
        if os.path.isdir(dir):
            latest_folder = os.path.getctime(dir)
            folder_time = datetime.fromtimestamp(latest_folder).strftime('%Y-%m-%d_%H:%M:%S')
            newdir = os.path.join(folder_time)
            """Prepare the new name for each image"""
            imagename = os.path.join('Pictures',newdir,'IMG_'+dt+'_4''.tiff')
            """Now demosaic the image using opencv; bear in mind that \
            our Bayer pattern is RGGB, so the second row and columns \
            are GR"""
            n = cv2.cvtColor(n, cv2.COLOR_BayerGR2RGB)
            """BayerGR2RGB will create an image with three channels, \
            so we need to transform them into a single channel image \
            again"""
            cv2.imwrite(imagename, n[:,:,0])
            print('Done!')
            return save_pic2


if __name__ == '__main__':
    new_folder()
    while True:
        input_value = GPIO.input(13)
        if input_value == False:
            print('Button Pressed... Proceeding with capture:')
            start_conn, save_conn = Pipe()
            start1_conn, save2_conn = Pipe()
            start = Process(target=start_cam1, args=(start_conn,))
            start1 = Process(target=start_cam2, args=(start1_conn,))
            save = Process(target=save_pic1, args=(save_conn,))
            save2 = Process(target=save_pic2, args=(save2_conn,))
            start.start()
            save.start()
            start1.start()
            save2.start()
            start.join()
