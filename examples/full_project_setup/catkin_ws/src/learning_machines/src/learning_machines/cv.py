import numpy as np
import cv2

from util import get_limits

cap = cv2.VideoCapture(2)

green = [0,255,0] 

while True:
    ret, frame = cap.read()

    hsvImage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lowerLimit, upperLimit = get_limits(color = green)

    mask = cv2.inRange(hsvImage, lowerLimit, upperLimit)

    cv2.imshow('frame', mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break