import os
from datetime import datetime



imagePath = os.path.join('.','Pictures')

if os.path.exists(imagePath):
    timestr = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    now = datetime.now()
    newDirName = now.strftime('%Y-%m-%d_%H:%M:%S')
    os.mkdir(os.path.join('Pictures',newDirName))
    print('Creating '+newDirName+' folder')
