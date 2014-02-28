import numpy as np
import cv2, time, serial, thread, draw, sys, player, viewcolor, sys, os, json, colorsys


height, width = (480, 640)
l3 = 80
l5 = 250
lb = width-40
llight = width-18

datas = []

def anaylze(frame, debug = False, start = 10):
  blue_start = -1
  notblue_start = 0
  notblue_end = 0
  viewcolor.setIndex(start)
  
  
  for i in range(start, width):
    r = frame.item(l3,i,2)
    g = frame.item(l3,i,1)
    b = frame.item(l3,i,0)
    viewcolor.rgb(r,g,b)
    
    (h,s,v) = colorsys.rgb_to_hsv(r/255.0,g/255.0,b/255.0)
    print "%f\t%f\t%f"%(h,s,v)
    
    if h > 0.45 and h < 0.6 and blue_start < 0:
      blue_start = i
    
    if blue_start >=0 and h < 0.45 and s > 0.75 and notblue_start == 0:
      notblue_start = i
      print notblue_start
  
  
  if debug:
    img = draw.start(frame)
    draw.line(img, (0,l3), (width,l3))
    draw.line(img, (notblue_start,0), (notblue_start,height))
    draw.line(img, (llight,0), (llight,height))
    draw.end(img)
    cv2.imshow('frame',frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if len(sys.argv) == 1:
  path = 'data'
else:
  path = "data_"+sys.argv[1]


def dd():
  frame = cv2.imread(path+'/1393489375.610911.jpg')
  viewcolor.start()
  anaylze(frame, True)
  viewcolor.end()
  exit(0)

dd()


if os.path.exists(path+"/t.json"):
  s = open(path+'/t.json').read()
  ts = json.loads(s)
  
  t1 = ts['t1']
  t2 = ts['t2']
  t3 = ts['t3']
else:
  t1=1393417396.83
  t2=t1
  t3=1393417399.73

fs = []


for f in os.listdir(path):
  if f.endswith('jpg'):
    fs.append(f)
fs.sort()

for f in fs:
  t = float(f.replace('.jpg',''))
  
  if t < t1 or t > t3:
    continue
  
  frame = cv2.imread(path+'/'+f)
  print f.replace('.jpg',''),"\t",
    
  if t > t2:
    anaylze(frame)
  else:
    anaylze(frame, False, l5)

is_down = True
last = 1000
pivots = []
for d in datas:
  if is_down and d > last:
    print d
    pivots.append(d)
    is_down = False
  elif (not is_down) and d < last:
    print d
    pivots.append(d)
    is_down = True
  
  last = d
  
if len(pivots) == 4:
  print 'fst jump:', pivots[1]-pivots[0]
  print 'sec jump:', pivots[3]-pivots[2]
  