import glob
import os
from datetime import datetime
from multiprocessing import Process, Pipe
import cv2
import numpy as np
import picamera.array
import picamera



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
    camera.sensor_mode = 1
    camera.iso = 100
    #sleep(0.6)
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g
    print('Starting capture')
    output = picamera.array.PiBayerArray(camera)
    camera.capture(output, 'jpeg', bayer=True)
    #debase = (output.demosaic() >> 2).astype(np.uint8)
    debase = ((output.array >>2).astype(np.uint8))
    conn.send(debase)


def start_cam2(conn):
    """Starts camera cs 1 in the Compute Module"""
    camera = picamera.PiCamera(1)
    camera.sensor_mode = 1
    camera.iso = 100
    #sleep(0.6)
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g
    print('Starting capture')
    output = picamera.array.PiBayerArray(camera)
    camera.capture(output, 'jpeg', bayer=True)
    #debase1 = (output.demosaic() >> 2).astype(np.uint8)
    debase = ((output.array >>2).astype(np.uint8))
    conn.send(debase)


def save_pic1(conn):
    """Saves RGB in three different channels"""
    dt = datetime.now().strftime("%M_%S.%f")[:-3]
    debase=conn.recv()
    r = debase[:,:,0]
    g = debase[:,:,1]
    b = debase[:,:,2]
    for dir in glob.glob('Pictures'):
        if os.path.isdir(dir):
            latest_folder = os.path.getctime(dir)
            folder_time = datetime.fromtimestamp(latest_folder).strftime('%Y-%m-%d_%H:%M:%S')
            newdir = os.path.join(folder_time)
            imagename1 = os.path.join('Pictures', newdir, 'IMG_'+dt+'_1''.tiff')
            imagename2 = os.path.join('Pictures', newdir, 'IMG_'+dt+'_2''.tiff')
            imagename3 = os.path.join('Pictures', newdir, 'IMG_'+dt+'_3''.tiff')
            r = cv2.cvtColor(r, cv2.COLOR_BayerGR2RGB)
            g = cv2.cvtColor(g, cv2.COLOR_BayerGR2RGB)
            b = cv2.cvtColor(b, cv2.COLOR_BayerGR2RGB)
            cv2.imwrite(imagename1, r[:,:,0])
            cv2.imwrite(imagename2, g[:,:,1])
            cv2.imwrite(imagename3, b[:,:,2])
            print('Done!')
            return save_pic1

def save_pic2(conn):
    """Saves the NIR band in one channel"""
    dt = datetime.now().strftime("%M_%S.%f")[:-3]
    debase1=conn.recv()
    n = debase1[:, :, 0]
    for dir in glob.glob('Pictures'):
        if os.path.isdir(dir):
            latest_folder = os.path.getctime(dir)
            folder_time = datetime.fromtimestamp(latest_folder).strftime('%Y-%m-%d_%H:%M:%S')
            newdir = os.path.join(folder_time)
            imagename = os.path.join('Pictures',newdir,'IMG_'+dt+'_4''.tiff')
            n = cv2.cvtColor(n, cv2.COLOR_BayerGR2RGB)
            cv2.imwrite(imagename, n[:,:,0])
            print('Done!')
            return save_pic2


if __name__ == '__main__':
    new_folder()
    start_conn, save_conn = Pipe()
    start1_conn, save2_conn = Pipe()
    start = Process(target=start_cam1, args=(start_conn,))
    start1 = Process(target=start_cam2, args=(start1_conn,))
    save = Process(target=save_pic1, args=(save_conn,))
    save2 = Process(target=save_pic2, args=(save2_conn,))
    start.start()
    start1.start()
    save.start()
    save2.start()
    start.join()
    save.join()
    start1.join()
    save2.join()
