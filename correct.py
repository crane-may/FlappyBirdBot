import numpy as np
import cv2, time, serial, thread, os, json, core
from Queue import *

cap = cv2.VideoCapture(1)
cap.set(3,640)
cap.set(4,480)

fps = 0
last_t = 0
while(True):
  fps += 1
  t = int(time.time())
  if t > last_t:
    print fps
    fps = 0
  last_t = t

  ret, frame = cap.read()
  
  cv2.line(frame, (int(core.GROUND_X) , 0), (int(core.GROUND_X), 480), (0,0,255), 1)
  cv2.line(frame, (0, int(core.B_Y)), (640, int(core.B_Y)), (0,0,255), 1)
  
  cv2.imshow('frame',frame)
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

