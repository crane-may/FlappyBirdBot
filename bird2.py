import numpy as np
import cv2, time, serial, thread, draw, sys, player

height, width = (480, 640)
l2 = height - 157
l4 = 80
la = 30
lb = width-70

V = 204.0
Tj = 0.30
J = 70.0 # 0.5 * G * (Tj**2)#71.0
G = 2.0* J/ ((0.595-Tj)**2)
B0 = 70.0
Bp = 20.0
Sb = l2 - l4
M = V*Tj
L = 80.0
H2_1 = 156.0
K = 1.0
pipe_queue = []
PipeTdelay = 0.10
Pipe_gap = 240.0
Bd = -10.0

h0 = 0.0
t0 = 0.0
H0 = 235.0

NO_LOG = False
LOGFILE = None
class LOG_CLASS:
  pass
LOG = LOG_CLASS()
LOG.l2 = l2
LOG.l4 = l4
LOG.la = la
LOG.lb = lb
LOG.b = 0
def log(b):
  global LOG
  LOG.b = b
  if not NO_LOG:
    LOGFILE.write("%f b %.01f l2 %.01f l4 %.01f la %.01f lb %.01f\n" % (time.time(),LOG.b,LOG.l2,LOG.l4,LOG.la,LOG.lb))
  
ser= serial.Serial("/dev/ttyUSB0",19200)

def drawFunc(frame, data):
  frame = draw.start(frame)
  draw.point(frame,(data.lb-int(data.b),l2),(0,0,0),5)
  
  draw.line(frame,(0,data.l2+2),(width,data.l2+2),(255,0,0),1)
  draw.line(frame,(0,data.l4+2),(width,data.l4+2),(255,0,0),1)
  draw.line(frame,(data.la,0),(data.la,height),(255,0,0),1)
  draw.line(frame,(data.lb,0),(data.lb,height),(255,0,0),1)
  draw.end(frame)
  
def proc_image(frame):
  if not NO_LOG:
    cv2.imwrite('data/%f.jpg'%time.time(),frame)
  drawFunc(frame, LOG)
  cv2.imshow('frame',frame)
  
def calc_b(t):
  global h0, t0, LOG
  
  if len(pipe_queue):
    p = pipe_queue[0]
    s = Sb - (time.time() - p['t'])*V
  else :
    s = 9
  
  delta_t = t - t0
  if delta_t < Tj:
    b = h0 + delta_t / Tj * J
  else:
    b = h0 + J - 0.5 * G * (delta_t - Tj) ** 2
  
  log(b)
  return b

def jump(b):
  global h0, t0, ser
  print "jumpppppppppppp", time.time()
  t0 = time.time()
  h0 = b
  ser.write("\n")
  time.sleep(0.10)
  

def pipe_append(new_h1):
  global pipe_queue
  p = {"h1": new_h1, "t": time.time() - PipeTdelay}
  
  if len(pipe_queue) > 0:
    p_cur = pipe_queue[0]
    
    if p['t'] - p_cur['t'] > Pipe_gap / V:
      pipe_queue.append(p)
  else:
    pipe_queue.append(p)


def action(b):
  global pipe_queue, PIPE, SURVIVE, CUR_S, STOP
  now = time.time()
    
  if len(pipe_queue) > 0:
    p = pipe_queue[0]
    h1 = p['h1']
    s = Sb - (now - p['t'])*V
    CUR_S = s
  else:
    h1 = -1
  
  if h1 < 0:
    if b <= B0:
      jump(b)
      
  elif s > 0:
    PIPE = h1
    SURVIVE = h1 - s*K + Bp
    if (h1 - b)/K < s + Bd  or  b <= B0:
      jump(b)
  
  elif L - 10 +s >= 0:
    SURVIVE = Bp + h1
    if b < Bp + h1:
      jump(b)
  
  else:
    pipe_queue = pipe_queue[1:]

def picturn_test():
  frame = cv2.imread("shot.png")
  
  proc_image(frame)
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

def run():
  global h0,H0,LOGFILE
  if not NO_LOG:
    LOGFILE = open('data/log','w')
  
  thread.start_new_thread(video_thread,())
  time.sleep(5)
  
  h0 = H0
  jump(H0)
  
  while True:
    t = time.time()
    b = calc_b(t)
    action(b)
    time.sleep(0.01)

def correct():
  global NO_LOG
  NO_LOG = True
  run()

def replay():
  p = player.Player(drawFunc)

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print 'usage: python bird2.py [run|picturn_test|replay|correct]' 
  else:
    eval("%s()"%sys.argv[1]) 
  
  
