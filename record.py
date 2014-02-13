import numpy as np
import cv2, time, serial, thread
from Queue import *

cap = cv2.VideoCapture(0)

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
  cv2.imwrite('data/%f.jpg'%time.time(),frame)
  cv2.imshow('frame',frame)
  
  if cv2.waitKey(1) & 0xFF == ord('q'):
    cv2.imwrite("shot.png", frame)
    break
    


