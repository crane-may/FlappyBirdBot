import numpy as np
import cv2, time, serial, thread, os, json, sys
from Queue import *

if len(sys.argv) != 2:
  print "usage: python rerord path"
  exit(0)

cap = cv2.VideoCapture(1)
cap.set(3,640)
cap.set(4,480)

fps = 0
last_t = 0
skip = 10

def jump():
  ser = serial.Serial("/dev/tty.usbmodemfd1311",19200)
  time.sleep(8)
  print time.time()
  ser.write("\n")

# thread.start_new_thread(jump,())

while(True):
  fps += 1
  t = int(time.time())
  if t > last_t:
    print fps
    fps = 0
  last_t = t

  ret, frame = cap.read()
  if skip > 0:
    skip -= 1
  else:
    cv2.imwrite(sys.argv[1]+'/%f.jpg'%time.time(),frame)
  
  cv2.imshow('frame',frame)
  
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

