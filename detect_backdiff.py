import numpy as np
import cv2, sys, time, os, serial, core, backdiff

diff_h = backdiff.Diff(5, 5)
diff_g = backdiff.Diff(25, 15)
diff_dark_h = backdiff.Diff(5, 5)
diff_dark_g = backdiff.Diff(25, 20)

green_mask = None

def init_back():
  global green_mask
  green_mask = cv2.imread("green_mask.jpg")
  green_mask = cv2.cvtColor(green_mask,cv2.COLOR_BGR2GRAY)
  ret, green_mask = cv2.threshold(green_mask, 40, 255, cv2.THRESH_BINARY)
  
  for f in os.listdir('learn_1'):
    if f.endswith('jpg'):
      frame = cv2.imread('learn_1/'+f)
      hsv = cv2.split(cv2.cvtColor(frame,cv2.COLOR_BGR2HSV))
      diff_h.acc_back(hsv[0])
      
      gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
      diff_g.acc_back(gray)
      
  diff_h.create_models_from_stats()
  diff_g.create_models_from_stats()

  for f in os.listdir('learn_2'):
    if f.endswith('jpg'):
      frame = cv2.imread('learn_2/'+f)
      hsv = cv2.split(cv2.cvtColor(frame,cv2.COLOR_BGR2HSV))
      diff_dark_h.acc_back(hsv[0])
      
      gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
      diff_dark_g.acc_back(gray)
      
  diff_dark_h.create_models_from_stats()
  diff_dark_g.create_models_from_stats()
  

init_back()

use_which_learn = None
def pre_frame(frame):
  global use_which_learn
  
  f = cv2.blur(frame, (3,3))
  hsv = cv2.split(cv2.cvtColor(f, cv2.COLOR_BGR2HSV))
  gray = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
  
  if use_which_learn == None:
    light = diff_g.background_diff(gray)
    dark = diff_dark_g.background_diff(gray)
    
    ld_mask = cv2.imread('light_dark_mask.jpg')
    ld_mask = cv2.cvtColor(ld_mask,cv2.COLOR_BGR2GRAY)
    ret, ld_mask = cv2.threshold(ld_mask, 40, 255, cv2.THRESH_BINARY)
    light = cv2.bitwise_and(light, ld_mask)
    dark =  cv2.bitwise_and(dark , ld_mask)
    
    # print "light", cv2.sumElems(light)
    # print "dark", cv2.sumElems(dark)
    
    light_ret = cv2.sumElems(light)
    dark_ret = cv2.sumElems(dark)
    
    if light_ret[0] > dark_ret[0]:
      print "============= night =============="
      use_which_learn = 2
    else:
      print "============= day =============="
      use_which_learn = 1
    
  if use_which_learn == 1:    
    mask_h = diff_h.background_diff(hsv[0])
    mask_h = cv2.bitwise_and(mask_h, green_mask)
    # cv2.imshow('frame2', mask_h)
    
    mask_g = diff_g.background_diff(gray)
    # cv2.imshow('frame3', mask_g)
  else:
    mask_h = diff_dark_h.background_diff(hsv[0])
    mask_h = cv2.bitwise_and(mask_h, green_mask)
    # cv2.imshow('frame2', mask_h)
    
    mask_g = diff_dark_g.background_diff(gray)
    # cv2.imshow('frame3', mask_g)
  
  return  cv2.bitwise_or(mask_g, mask_h)


def bird_h(frame, detect_b_y, ground_x, pipe_space):
  blue_start = -1
  notblue_start = 0
  notblue_end = 0
    
  blue_starts = []
  for j in range(-10, 11, 10):
    for i in range(10, int(ground_x-10)):
      b = frame.item(detect_b_y+j,i)
      if b == 0:
        blue_starts.append(i)
        break
    
  blue_start = max(blue_starts)
  
  if blue_start > 15:
    for j in [-20,20]:
      for i in range(10, int(ground_x-10)):
        b = frame.item(detect_b_y+j,i)

        if b == 0:
          blue_starts.append(i)
          break
    
    blue_start = max(blue_starts)
  
  red_yellow_ends = []
  red_yellow_end = 0
  
  for i in range(int(blue_start), int(ground_x-20)):
    b = frame.item(detect_b_y,i)
    
    if blue_start > 15 and i > blue_start + pipe_space - 10:
      break
    
    if b > 0:
      red_yellow_end = i
    
    red_yellow_ends.append(red_yellow_end)
  
  red_yellow_end = max(red_yellow_ends)
  if red_yellow_end > 10 and red_yellow_end < ground_x - 10:
    return ground_x - red_yellow_end
  else:
    return -1
  

def pipe_h(frame, pipe_space, detect_pipe_y, detect_pipe_top_x, ground_x, pipe_w, pipe_v, delay):
  for i in range(int(detect_pipe_top_x), int(detect_pipe_top_x+15)):
    b = frame.item(detect_pipe_y,i)
    if b == 0:
      return (-1,-1)
 
  pipe_x = 0
  for i in range(int(detect_pipe_top_x), int(ground_x-20)):
    b = frame.item(detect_pipe_y,i)
    if b == 0:
      pipe_x = i
      break
     
  pipe_y = 0
  for i in range(int(detect_pipe_y), int(detect_pipe_y) + int(pipe_w)):
    b = frame.item(i,pipe_x-5)
    if b == 0:
      if i < detect_pipe_y + 10:
        return (-1,-1)
      else:
        pipe_y = i
        break
  
  if pipe_x > 0 and pipe_y > 0:
    ret = ground_x - pipe_x - pipe_space
    ret += (320 - pipe_x)/273.0 *10.0
    return (ret, time.time() - (pipe_y-detect_pipe_y)/pipe_v - delay)
  else:
    return (-1,-1)
      
def timer():
  return 0.06

def on_mouse(event, x, y, flags, ps):
  if event == cv2.EVENT_LBUTTONDOWN:
      print 'Mouse Position: ',x,y
      
      print 'R:',frame.item(y, x, 2),
      print 'G:',frame.item(y, x, 1),
      print 'B:',frame.item(y, x, 0)

      hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
      print 'H:',hsv.item(y, x, 0),
      print 'S:',hsv.item(y, x, 1),
      print 'V:',hsv.item(y, x, 2)

if __name__ == '__main__':
  cv2.namedWindow('frame1')
  cv2.namedWindow('frame2')
  cv2.namedWindow('frame3')
  cv2.namedWindow('frame4')
  cv2.moveWindow('frame1', 0,0)
  cv2.moveWindow('frame2', 700,0)
  cv2.moveWindow('frame3', 1400,0)
  cv2.moveWindow('frame4', 0,700)
  cv2.setMouseCallback('frame1', on_mouse, 0)

  files = []
  for f in os.listdir('/Volumes/RamDisk/datalog'):
    if f.endswith('jpg'):
      files.append("/Volumes/RamDisk/datalog/"+f)
  
  i = 0
  while i < len(files):
    frame = cv2.imread(files[i])
    
    frame2 = pre_frame(frame)
    b = bird_h(frame2, core.DETECT_BIRD_Y, core.GROUND_X, core.PIPE_SPACE)
    p, t = pipe_h(frame2, core.PIPE_SPACE, core.DETECT_PIPE_Y, core.DETECT_PIPE_TOP_X, core.GROUND_X, core.PIPE_W, core.PIPE_V, timer())
    
    cv2.line(frame2, (0,int(core.DETECT_BIRD_Y)), (640,int(core.DETECT_BIRD_Y)), (128), 1)
    if b > 0:
      cv2.line(frame2, (int(core.GROUND_X-b), 0), (int(core.GROUND_X-b), 480), (128), 1)
    
    cv2.line(frame2, (0,int(core.DETECT_PIPE_Y)), (640,int(core.DETECT_PIPE_Y)), (255), 1)
    if p > 0:
      cv2.line(frame2, (int(core.GROUND_X-p), 0), (int(core.GROUND_X-p), 480), (255), 1)
    
    cv2.imshow('frame1', frame)
    cv2.imshow('frame4', frame2)
    
    c = cv2.waitKey(0)
    if c == 63235: #next
      pass
    elif c == 63234: #prev
      i -= 2
    elif c == 63233: #down
      i += 10
    elif c == 63232: #up
      i -= 11
    elif c == ord('q'):
      break
    
    i += 1
    