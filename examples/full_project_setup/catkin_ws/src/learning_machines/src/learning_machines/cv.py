import numpy as np
import cv2
from .robobo_env import RoboboEnv

from robobo_interface import HardwareRobobo
from util import get_limits

def get_processed_image_front():

    frame = HardwareRobobo.get_image_front()

    green = [0, 255, 0]  
    
    hsvImage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    lowerLimit, upperLimit = get_limits(color=green)
    mask = cv2.inRange(hsvImage, lowerLimit, upperLimit)

    return frame, mask  

while True:
    
    frame, mask = get_processed_image_front()
    
    if frame is not None:
        cv2.imshow('frame', mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


# this worked on my computer idk if the code above works for robobo hopefully it does and it should detect green if it does it should show white on the screen
# cap = cv2.VideoCapture(0)

# green = [0,255,0] 

# while True:
#     ret, frame = cap.read()

#     hsvImage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

#     lowerLimit, upperLimit = get_limits(color = green)

#     mask = cv2.inRange(hsvImage, lowerLimit, upperLimit)

#     cv2.imshow('frame', mask)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()

# cv2.destroyAllWindows()