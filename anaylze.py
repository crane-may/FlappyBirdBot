import numpy as np
import cv2, time, serial, thread, draw, sys, player, viewcolor, sys, os


height, width = (480, 640)
l3 = height - 124
l5 = 250

def anaylze(frame, debug = False, start = 10):
  notblue_start = 0
  notblue_end = 0
  viewcolor.setIndex(start)
  
  for i in range(start, width):
    r = frame.item(l3,i,2)
    g = frame.item(l3,i,1)
    b = frame.item(l3,i,0)
    viewcolor.rgb(r,g,b)
    vb = b + b - r - g
    vg = g + g - r - b
    
    if (vb < 5 or vg < 5) and notblue_start == 0:
      if debug:
        print r,g,b,vb,vg
      notblue_start = i
    elif (vb > 40 or vg > 100) and notblue_start > 0 and notblue_end == 0:
      if debug:
        print r,g,b,vb,vg
      notblue_end = i
  
  if notblue_end - notblue_start < 75 and notblue_end - notblue_start > 30:  
    print (notblue_start+notblue_end)/2.0
  else:
    print 'xxxxxxx'
  
  if debug:
    print notblue_start,'---' ,notblue_end, notblue_end - notblue_start
    img = draw.start(frame)
    draw.line(img, (0,l3), (width,l3))
    draw.line(img, (l5,0), (l5,height), (255,0,0))
    draw.line(img, (notblue_start,0), (notblue_start,height))
    draw.line(img, (notblue_end,0), (notblue_end,height))
    draw.line(img, ((notblue_start+notblue_end)/2.0,0), ((notblue_start+notblue_end)/2.0,height))
    draw.end(img)
    cv2.imshow('frame',frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def dd():
  frame = cv2.imread('data/1393002416.962718.jpg')
  viewcolor.start()
  anaylze(frame, True,l5)
  viewcolor.end()
  exit(0)

dd()

t1=1393002414.886988
t2=1393002416.583580
t3=1393002416.962718
fs = []
for f in os.listdir("data_"+sys.argv[1]):
  if f.endswith('jpg'):
    fs.append(f)
fs.sort()

for f in fs:
  t = float(f.replace('.jpg',''))
  
  if t < t1 or t > t3:
    continue
  
  frame = cv2.imread('data/'+f)
  print f.replace('.jpg',''),
    
  if t > t2:
    anaylze(frame)
  else:
    anaylze(frame, False, l5)
    

