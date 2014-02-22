import numpy as np
import cv2, time, serial, thread, draw, sys, player, viewcolor, sys

height, width = (480, 640)
l2 = height - 157
l3 = height - 124
l4 = 80
la = 15
lb = width-40

V = 217.0 # replay to measure
#Tj = 0.29605 # flatten fly to measure
#J = 78.0 # replay to measure
Tj = 0.29605 # flatten fly to measure
J = 82.0 # replay to measure
G = 2.0* J/ (Tj**2)
PipeTdelay = 0.15# replay to measure
B0 = 70.0
Bp = 48.0
Sb = l2 - l4
M = V*Tj
L = 95.0 
H2_1 = 168.0
K = 1.0
Pipe_gap = 240.0
Bd = 30.0
Jump_sleep = 0.20
H0 = 258.0
Addon_gap = Pipe_gap / V
Bird_body = 40.0

# BUG. not atomic operate
pipe_queue = []

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
  

def drawFunc(frame, d):
  frame = draw.start(frame)
  # static
  draw.line(frame,(0,d.l2+2),(width,d.l2+2),(255,0,0),1)
  draw.line(frame,(0,d.l3+2),(width,d.l3+2),(255,0,255),1)
  draw.line(frame,(0,d.l4+2),(width,d.l4+2),(255,0,0),1)
  draw.line(frame,(d.la,0),(d.la,height),(255,0,0),1)
  draw.line(frame,(d.lb,0),(d.lb,height),(255,0,0),1)
  
  # bird
  draw.point(frame,(d.lb-d.b,l2),(0,0,0),5)
  draw.line(frame,(d.lb-d.b,0),(d.lb-d.b,height),(0,0,0),1)
  
  # pipe
  draw.line(frame,(d.lb-d.h1,d.l2-d.s),(d.lb,d.l2-d.s),(255,255,0),1)
  draw.line(frame,(d.lb-d.h1,d.l2-d.s),(d.lb-d.h1,d.l2-d.s-L-Bird_body),(255,255,0),1)
  
  # survival
  draw.line(frame,(d.lb-d.sur,d.l2),(d.lb-d.sur+10,d.l2+10),(0,255,255),1)
  
  draw.end(frame)
  
def proc_image(frame):
  if not NO_LOG:
    cv2.imwrite('data/%f.jpg'%time.time(),frame)
  pipe_sensor(frame)
  drawFunc(frame, LOG)
  cv2.imshow('frame',frame)
  
######################################################

#ser= serial.Serial("/dev/ttyUSB0",19200)
def jump(b):
  print "jump", time.time()
#  ser.write("\n")
  
######################################################

def calc_b(t, b_last_jump2, t_last_jump):
  global b_last_jump
#  print t,b_last_jump,t_last_jump
  delta_t = t - t_last_jump
  if delta_t > 0.728:
    print '********'
    g = G - 12*(delta_t+0.172)
  else :
    g = G
  g = G
  b = b_last_jump + J - 0.5 * g * (delta_t - Tj) ** 2
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
  global last_addon, pipe_queue, b_last_jump
  
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
  ret, frame = cap.read()
  
  while(True):
    ret, frame = cap.read()
    proc_image(frame)
    cv2.waitKey(3)

  cap.release()
  cv2.destroyAllWindows()
  exit(0)

b_last_jump = 0
def run():
  global h0,LOGFILE,b_last_jump
  if not NO_LOG:
    LOGFILE = open('data/log','w')
  
  thread.start_new_thread(video_thread,())
  time.sleep(5)
  
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
      t_last_jump = t
      b_last_jump = b
      jump(b)
    
    log(t,b,h1,s,sur)
    time.sleep(0.01)

def correct():
  global NO_LOG
  NO_LOG = True
  run()

def test_jump():
  global h0,LOGFILE,b_last_jump
  if not NO_LOG:
    LOGFILE = open('data/log','w')
  
  thread.start_new_thread(video_thread,())
  time.sleep(5)
  
  b = H0
  log(time.time(),b,0,0,0)
  t_last_jump = time.time()
  b_last_jump = b
  jump(b)
  
  jump_count=1
  while True:
    t = time.time()
    b = calc_b(t, b_last_jump, t_last_jump)
    
    if (jump_count > 1 and jump_count < 7 and t - t_last_jump > 0.20) or \
       (jump_count == 1 and t - t_last_jump > 0.85):
      t_last_jump = t
      b_last_jump = b
      jump_count+=1
      jump(b)
    
    log(t,b,0,0,0)
    time.sleep(0.01)

def test_flatten():
  global h0,LOGFILE,b_last_jump
  if not NO_LOG:
    LOGFILE = open('data/log','w')
  
  thread.start_new_thread(video_thread,())
  time.sleep(5)
  
  b = H0
  log(b,0,0,0,0)
  t_last_jump = time.time()
  b_last_jump = b
  jump(b)
  
  while True:
    t = time.time()
    if t - t_last_jump >= 2.0 * Tj:
      t_last_jump = t
      jump(b)
    log(t,b,0,0,0)
    time.sleep(0.01)

def replay():
  p = player.Player(drawFunc, lb, l2, 0.16)

if __name__ == '__main__':
  if os.path.exists('data'):
    os.mkdir('data')
    
  if len(sys.argv) < 2:
    print 'usage: python bird2.py [run|picture|replay|correct]' 
  else:
    eval("%s()"%sys.argv[1]) 
  
  
