import cv2, time, colorsys


def bird_h(frame, detect_b_y, ground_x, pipe_space):
  blue_start = -1
  notblue_start = 0
  notblue_end = 0
  
  # bottoms = []
  # for j in range(-15,16,5):
    # print '-----------'
  
  blue_starts = []
  for j in range(-10, 11, 10):
    for i in range(10, int(ground_x-10)):
      r = frame.item(detect_b_y+j,i,2)
      g = frame.item(detect_b_y+j,i,1)
      b = frame.item(detect_b_y+j,i,0)

      (h,s,v) = colorsys.rgb_to_hsv(r/255.0,g/255.0,b/255.0)
      if h > 0.45 and h < 0.6:
        blue_starts.append(i)
        break
    
  blue_start = max(blue_starts)
  
  if blue_start > 15:
    for j in [-20,20]:
      for i in range(10, int(ground_x-10)):
        r = frame.item(detect_b_y+j,i,2)
        g = frame.item(detect_b_y+j,i,1)
        b = frame.item(detect_b_y+j,i,0)

        (h,s,v) = colorsys.rgb_to_hsv(r/255.0,g/255.0,b/255.0)
        if h > 0.45 and h < 0.6:
          blue_starts.append(i)
          break
    
    blue_start = max(blue_starts)
  
  red_yellow_ends = []
  for j in [-15,0]:
    red_yellow_end = 0
    for i in range(int(blue_start), int(ground_x-20)):
      r = frame.item(detect_b_y,i,2)
      g = frame.item(detect_b_y,i,1)
      b = frame.item(detect_b_y,i,0)

      (h,s,v) = colorsys.rgb_to_hsv(r/255.0,g/255.0,b/255.0)
      # print "%f\t%f\t%f"%(h,s,v)
    
      if blue_start > 15 and i > blue_start + pipe_space - 10:
        break
    
      if h < 0.20:
        red_yellow_end = i
    
    red_yellow_ends.append(red_yellow_end)
  
  red_yellow_end = max(red_yellow_ends)
  if red_yellow_end > 10 and red_yellow_end < ground_x - 10:
    return ground_x - red_yellow_end + 10
  else:
    return -1
  
  
def pipe_h(frame, pipe_space, detect_pipe_y, detect_pipe_top_x, ground_x, pipe_w, pipe_v, delay):
   for i in range(int(detect_pipe_top_x), int(detect_pipe_top_x+15)):
     r = frame.item(detect_pipe_y,i,2)
     g = frame.item(detect_pipe_y,i,1)
     b = frame.item(detect_pipe_y,i,0)
     (h,s,v) = colorsys.rgb_to_hsv(r/255.0,g/255.0,b/255.0)
     
     if h > 0.4:
       return (-1,-1)
  
   pipe_x = 0
   for i in range(int(detect_pipe_top_x), int(ground_x-20)):
     r = frame.item(detect_pipe_y,i,2)
     g = frame.item(detect_pipe_y,i,1)
     b = frame.item(detect_pipe_y,i,0)
     (h,s,v) = colorsys.rgb_to_hsv(r/255.0,g/255.0,b/255.0)
    
     if h > 0.4:
       pipe_x = i
       break
      
   pipe_y = 0
   for i in range(int(detect_pipe_y), int(detect_pipe_y) + int(pipe_w)):
     r = frame.item(i,pipe_x-5,2)
     g = frame.item(i,pipe_x-5,1)
     b = frame.item(i,pipe_x-5,0)
     (h,s,v) = colorsys.rgb_to_hsv(r/255.0,g/255.0,b/255.0)
    
     if h > 0.4:
       if i < detect_pipe_y + 5:
         return (-1,-1)
       else:
         pipe_y = i
         break
   
   if pipe_x > 0 and pipe_y > 0:
     return (ground_x - pipe_x - pipe_space, time.time() - (pipe_y-detect_pipe_y)/pipe_v - delay)
   else:
     return (-1,-1)
  
  
def timer(frame, detect_timer_x):
  return 0.1
  
  t = 0
  for j in range(5):
    for i in range(j*55, (j+1)*55):
      r = frame.item(i,detect_timer_x,2)
      g = frame.item(i,detect_timer_x,1)
      b = frame.item(i,detect_timer_x,0)
      
      if r > 150:
        t |= (1 << (4 - j))
        break
  
  if t > 25:
    return -1
  else:
    now_org = time.time()
    now = int(now_org * 100) % 100
    now0 = int(now / 25) * 25
    now_25 = now % 25
    
    if t > now_25:
      t = now0 - 25 + t
    else:
      t = now0 + t
    
    t = t /100.0
    t = int(now_org) + t
    
    delta_t = now_org - t
    return delta_t

