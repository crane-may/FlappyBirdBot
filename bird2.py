import numpy as np
import cv2, time, serial, thread, draw, sys, player, viewcolor, sys, os, json, colorsys

#camera distance = 19cm

height, width = (480, 640)
l2 = height - 157
l3 = height - 120
l4 = 80
la = 15
lb = width-40
llight = width-18

V = 218.0 # replay to measure
#Tj = 0.29605 # flatten fly to measure
#J = 78.0 # replay to measure
Tj = 0.29605 # flatten fly to measure
J = 82.0 # replay to measure
G = 2.0* J/ (Tj**2)
PipeTdelay = 0.20# replay to measure
B0 = 70.0
Bp = 41.5
Sb = l2 - l4
M = V*Tj
L = 95.0 
H2_1 = 168.0
K = 1.0
Pipe_gap = 240.0
Bd = 20.0
Jump_sleep = 0.20
H0 = 258.0
Addon_gap = Pipe_gap / V
Bird_body = 43.0

# BUG. not atomic operate
pipe_queue = []
last_correct_bird = 0

NO_LOG = False
LOGFILE = None
class LOG_CLASS:
  pass
LOG = LOG_CLASS()
LOG.l2 = l2
LOG.l3 = l3
LOG.l4 = l4
LOG.la = la
LOG.lb = lb
LOG.llight = llight
LOG.b = 0
LOG.h1 = 0
LOG.s = 0
LOG.sur = 0
def log(t, b, h1, s, sur):
  global LOG
  LOG.b = b
  LOG.h1 = h1
  LOG.s = s
  LOG.sur = sur
  if not NO_LOG:
    LOGFILE.write("%f b %.01f h1 %.01f s %.01f sur %.01f l2 %.01f l3 %.01f l4 %.01f la %.01f lb %.01f\n" % (
                t,LOG.b,  LOG.h1,  LOG.s,  LOG.sur,  LOG.l2,  LOG.l3,  LOG.l4,  LOG.la,  LOG.lb))
  

def drawFunc(frame, d, path):
  frame = draw.start(frame)
  
  # bird_anaylze
  draw.point(frame,(lb-anaylze_bird_pos(draw.cvImg(frame,path)),l3),(0,255,255),5)
  
  # static
  draw.line(frame,(0,d.l2+2),(width,d.l2+2),(255,0,0),1)
  draw.line(frame,(0,d.l3+2),(width,d.l3+2),(255,0,255),1)
  draw.line(frame,(0,d.l4+2),(width,d.l4+2),(255,0,0),1)
  draw.line(frame,(d.la,0),(d.la,height),(255,0,0),1)
  draw.line(frame,(d.lb,0),(d.lb,height),(255,0,0),1)
  # draw.line(frame,(d.llight,0),(d.llight,height),(0,255,255),1)
  
  # bird
  draw.point(frame,(d.lb-d.b,l2),(0,0,0),5)
  draw.line(frame,(d.lb-d.b,0),(d.lb-d.b,height),(0,0,0),1)
  
  # pipe
  draw.line(frame,(d.lb-d.h1,d.l2-d.s),(d.lb,d.l2-d.s),(255,255,0),1)
  draw.line(frame,(d.lb-d.h1,d.l2-d.s),(d.lb-d.h1,d.l2-d.s-L-Bird_body),(255,255,0),1)
  
  # survival
  draw.line(frame,(d.lb-d.sur-50,d.l2-50),(d.lb-d.sur+50,d.l2+50),(0,255,255),1)
  
  draw.end(frame)
  
def proc_image(frame):
  if not NO_LOG:
    cv2.imwrite('data/%f.jpg'%time.time(),frame)
  pipe_sensor(frame)
  drawFunc(frame, LOG,'')
  cv2.imshow('frame',frame)
  
######################################################

ser= serial.Serial("/dev/tty.usbmodem1d1141",19200)
def jump(b):
  print "jump", time.time()
  ser.write("\n")
  
######################################################

b_history = []
need_correct = False

model_datas = json.loads(open('model.json').read())
def calc_b2(t, b_last_jump2, t_last_jump):
  global b_last_jump, b_history
  delta_t = t - t_last_jump
  ds = model_datas
  
  for j in range(0,len(ds),2):
    if delta_t < ds[j] and j > 0:
      pos1 = ds[j-1]
      pos2 = ds[j+1]
      pos = (delta_t-ds[j-2])/(ds[j]-ds[j-2])*(pos2 - pos1) + pos1
      
      b = pos+b_last_jump+calc_b_addon(delta_t)
      
      b_history.append((t,b))
      if b_history[0][0] + 0.18 < t:
        b_history = b_history[1:]
      return b
  
  return -10

def calc_b_addon(delta_t):
  if delta_t > 0.55 and delta_t <= 0.83:
    return 34.0 * delta_t**2 - 52.04 * delta_t + 20.1706
  elif delta_t > 0.83:
    return 44.0 * delta_t**2 - 65.64 * delta_t + 25.7696
  else:
    return 0

def calc_jump_addon(t_last_jump, t):
  if t - t_last_jump > 0.7:
    return -30
  else:
    return 0

def calc_b(t, b_last_jump2, t_last_jump):
  global b_last_jump, b_history, need_correct
  delta_t = t - t_last_jump
  b = b_last_jump + J - 0.5 * G * (delta_t - Tj) ** 2
  b += calc_b_addon(delta_t)
  
  if delta_t > 0.6:
    need_correct = True
  
  b_history.append((t,b))
  if b_history[0][0] + 0.25 < t:
    b_history = b_history[1:]
  return b

def calc_pipe_s(t, p):
  return Sb - (t - p['t'])*V

def calc_pipe(t):
  global pipe_queue
  if len(pipe_queue) > 0:
    p = pipe_queue[0]
    h1 = p['h1']
    s = calc_pipe_s(t, p)
    return (h1, s)
  else:
    return (-100,-100)

def calc_survival(t,b,h1,s,t_last_jump):
  global pipe_queue
  survival = 0
  
  # in raise
  if t < t_last_jump + Jump_sleep:
    survival = -25
  
  # no pipe
  elif h1 < 0:
    survival = B0
  
  # close pipe
  elif s > 20:
    survival = max(h1 - (s-Bd)*K, B0)
  
  # in pipe
  elif L + s + Bird_body >= 0: #bird_body
    survival = Bp + h1
  
  # leave pipe
  else:
    pipe_queue = pipe_queue[1:]
    survival = -50     
  
  return survival

def anaylze_bird_pos(frame):
  blue_start = -1
  notblue_start = 0
  notblue_end = 0
  
  for i in range(10, width):
    r = frame.item(l3,i,2)
    g = frame.item(l3,i,1)
    b = frame.item(l3,i,0)
    
    (h,s,v) = colorsys.rgb_to_hsv(r/255.0,g/255.0,b/255.0)
    # print "%f\t%f\t%f"%(h,s,v)
    
    if h > 0.45 and h < 0.6 and blue_start < 0:
      blue_start = i
    
    if blue_start >=0 and h < 0.45 and s > 0.75 and notblue_start == 0:
      notblue_start = i
      return lb - notblue_start - 20.0
  
  return 0

def anaylze_light(frame):
  t = 0
  for j in range(5):
    for i in range(j*55, (j+1)*55):
      r = frame.item(i,llight,2)
      g = frame.item(i,llight,1)
      b = frame.item(i,llight,0)
      
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

#########################################################

def pipe_pos2(frame, w ,l):
  pipe_top_avg = 0
  for i in range(la, la+15): 
    r = frame.item(l,i,2)
    g = frame.item(l,i,1)
    b = frame.item(l,i,0)
    pipe_top_avg += b + b - r - g - 1
  
  if pipe_top_avg > 0:
    return (-1,-1)
  
  pipe_x = 0
 # print "========="
  for i in range(la, lb-20):
    r = frame.item(l,i,2)
    g = frame.item(l,i,1)
    b = frame.item(l,i,0)
    v = b + b - r - g
    
   # print i, v
    if v > 5:
      pipe_x = i
      break
  #print "=======end======="
      
  pipe_y = 0
  for i in range(l, l + int(L)):
    r = frame.item(i,pipe_x-5,2)
    g = frame.item(i,pipe_x-5,1)
    b = frame.item(i,pipe_x-5,0)
    v = b + b - r - g
    
    if v > 5:
      if i < l + 5:
        return (-1,-1)
      else:
        pipe_y = i
        break
   
  if pipe_x > 0 and pipe_y > 0:
    return (pipe_x, time.time() - (pipe_y-l)/V - PipeTdelay)
  else:
    return (-1,-1)
  
def pipe_bird_pos(frame):
  pipe_top_avg = 0
  for i in range(la, la+15): 
    r = frame.item(l3,i,2)
    g = frame.item(l3,i,1)
    b = frame.item(l3,i,0)
    pipe_top_avg += b + b - r - g - 1
  
  if pipe_top_avg > 0:
    return -1
  
  pipe_x = 0
 # print "========="
  for i in range(la, lb-20):
    r = frame.item(l3,i,2)
    g = frame.item(l3,i,1)
    b = frame.item(l3,i,0)
    v = b + b - r - g
    
   # print i, v
    if v > 5:
      pipe_x = i
      break
  
  pipe_y = 0
  for i in range(l3-10, l3):
    r = frame.item(i,pipe_x-5,2)
    g = frame.item(i,pipe_x-5,1)
    b = frame.item(i,pipe_x-5,0)
    v = b + b - r - g
    
    if v > 5:
      return -1
  
  if pipe_x > 0:
    for i in range(pipe_x, int(pipe_x + H2_1)):
      r = frame.item(l3,i,2)
      g = frame.item(l3,i,1)
      b = frame.item(l3,i,0)
      v = b + b - r - g
      
      viewcolor.rgb(r,g,b)
      if v < -10 and not (r > 100 and g > 100 and b > 100):
        return i-pipe_x
  
  return -1

def bird_pos():
  pass

last_addon = 0
def pipe_sensor(frame):
  global last_addon, pipe_queue, b_last_jump, last_correct_bird, need_correct
  
  try:
    (pipe,t) = pipe_pos2(frame, width, l4)
  except Exception, e:
    print e
    (pipe,t) = (-1,-1)
 
  if pipe > 0:
    p = {"h1": (lb - pipe - H2_1)*1.0, "t": t}
    
    if len(pipe_queue) > 0:
      p_cur = pipe_queue[-1]
      
      if p['t'] - p_cur['t'] > Pipe_gap / V:
        print 'pipe2',time.time()
        pipe_queue.append(p)
    else:
      print 'pipe1',time.time()
      pipe_queue.append(p)
  
  #########
  
  
  delta_delay = anaylze_light(frame) + 0.08
  if delta_delay > 0 and delta_delay < 0.2:
    bird_pos = anaylze_bird_pos(frame)
    now = time.time()
    if len(b_history) > 0 and now - last_correct_bird > 0.17 and need_correct:
      need_correct = False
      
      h_cur = None
      for h in b_history:
        if now - delta_delay <= h[0]:
          h_cur = h
          break
      
      if h_cur != None:      
        dt = time.time() - h_cur[0]
    
        if dt > 0.05 and dt < 0.2:
          db = bird_pos - h_cur[1]
          if abs(db) < 60:
            if db > 10:
              db = 10
            if db < -10:
              db = -10
            b_last_jump += db
            print '&&&&&&&&&&&', db, h_cur[1], bird_pos, now, delta_delay
            last_correct_bird = now
  
  ##########
  
  return
  try:
    bird_top = pipe_bird_pos(frame)
  except Exception, e:
    print e
    bird_top = -1
  
  if time.time() > last_addon + Addon_gap:
    if bird_top > 110 and bird_top < 130:
      print '----------bottom----------',time.time(),bird_top,(20 - (H2_1 - bird_top - 40))*1.5
      b_last_jump -= (20 - (H2_1 - bird_top - 40))*1.5
      last_addon = time.time()
    elif bird_top < 20 and bird_top > 0:
      b_last_jump += (20 - bird_top)*1.5
      last_addon = time.time()
      print '----------top----------',time.time(),bird_top,(20 - bird_top)*1.5

#########################################################

  
def picture():
  global NO_LOG
  NO_LOG = True
  
  frame = cv2.imread(sys.argv[2])
  
  viewcolor.start()
  proc_image(frame)
  viewcolor.end()
  
  if len(pipe_queue) > 0:
    p = pipe_queue[0]
    log(0,0,p['h1'],calc_pipe_s(time.time(), p),0)
    proc_image(frame)
  else:
    print 'no pipe'

  cv2.waitKey(0)
  cv2.destroyAllWindows()
  

def video_thread():
  cap = cv2.VideoCapture(0)
  cap.set(3,640)
  cap.set(4,480)
  ret, frame = cap.read()
  
  while(True):
    ret, frame = cap.read()
    proc_image(frame)
    cv2.waitKey(1)

  cap.release()
  cv2.destroyAllWindows()
  exit(0)

def calc_thread():
  global h0,LOGFILE,b_last_jump
  time.sleep(4)
  
  tt = int(time.time())
  while True:
    if int(time.time()) > tt:
      ser.write(" ")
      break
    time.sleep(0.001)
  
  time.sleep(2)
  
  b = H0
  log(time.time(),b,0,0,0)
  t_last_jump = time.time()
  b_last_jump = b
  jump(b)
    
  while True:
    t = time.time()
    b = calc_b(t, b_last_jump, t_last_jump)
    (h1,s) = calc_pipe(t)
    sur = calc_survival(t,b,h1,s,t_last_jump)
    
    if b <= sur:
      b_last_jump = b #+ calc_jump_addon(t_last_jump, t)
      t_last_jump = t
      jump(b)
    
    log(t,b,h1,s,sur)
    time.sleep(0.01)

b_last_jump = 0
def run():
  global h0,LOGFILE,b_last_jump
  if not NO_LOG:
    LOGFILE = open('data/log','w')
  
  thread.start_new_thread(calc_thread,())
  video_thread()

def correct():
  global NO_LOG
  NO_LOG = True
  run()

def replay():
  if len(sys.argv) == 2:
    p = player.Player(drawFunc, lb, l2, 0.18)
  else:
    p = player.Player(drawFunc, lb, l2, 0.18, sys.argv[2])

if __name__ == '__main__':
  if not os.path.exists('data'):
    os.mkdir('data')
    
  if len(sys.argv) < 2:
    print 'usage: python bird2.py [run|picture|replay|correct]' 
  else:
    eval("%s()"%sys.argv[1]) 
  
  
