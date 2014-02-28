import numpy as np
import cv2, time, serial, thread, os, json
from Queue import *

EXIT = False

if not os.path.exists('data'):
  os.mkdir('data')

ser= serial.Serial("/dev/tty.usbmodem1d1141",19200)
def jump():
  print "#################",time.time()
  ser.write("\n")
  print "----------------------",time.time()

def do_jump():
  global EXIT
  
  time.sleep(6)
  jump()
  
  # time.sleep(0.6)
  # 
  # t1 = time.time()+0.20-0.20
  # print 't1', t1
  # jump()
  # time.sleep(0.25)
  # jump()
  # time.sleep(0.25)
  # jump()
  # 
  # time.sleep(1.0)
  # 
  # jump()
  # time.sleep(0.25)
  # jump()
  # time.sleep(0.25)
  # jump()
  # 
  # time.sleep(0.7)
  # t3 = time.time()+0.20
  # print 't3', t3
  # time.sleep(0.3)
  # 
  # f = open('data/t.json','w')
  # f.write(json.dumps({'t1':t1,'t2':t1,'t3':t3}))
  # f.close()
  # EXIT = True
  
  
thread.start_new_thread(do_jump,())

cap = cv2.VideoCapture(0)
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
  cv2.imwrite('data/%f.jpg'%time.time(),frame)
  cv2.imshow('frame',frame)
  
  if EXIT:
    exit(0)
    
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

