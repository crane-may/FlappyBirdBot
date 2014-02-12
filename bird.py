import numpy as np
import cv2, time, serial, thread

STOP = False

height, width = (480, 640)
l2 = height - 157
l4 = 80
la = 30
lb = width-70

#ser= serial.Serial("/dev/ttyUSB0",19200)

def proc_image(frame):
#  bird = bird_pos(frame, width, l2)
  pipe = pipe_pos(frame, width, l4)
  
  if pipe > 0:
    h1 = (lb - pipe - H2_1)*1.0
    pipe_append(h1)
  
  if len(pipe_queue):
    h1_ = pipe_queue[0]['h1']
    cv2.line(frame,(lb-int(PIPE),l2-int(CUR_S-Bd)),(int(lb-PIPE+h1_),int(l2-CUR_S+h1_/K+Bd)),(255,255,0),4)
    cv2.line(frame, (int(lb-PIPE-Bp),0),(int(lb-PIPE-Bp),height),(255,255,0),4)
    
  cv2.line(frame, (lb-int(B0),0),(lb-int(B0),height),(255,255,0),4)
  cv2.circle(frame,(lb-int(BIRD),l2),5,(0,0,0),5)
  
  cv2.rectangle(frame,(lb-int(PIPE),l2-int(CUR_S)),(width,0),(255,0,0),3)
  
  
#  cv2.line(frame,(lb-int(SURVIVE),0),(lb-int(SURVIVE),height),(255,255,0),1)
  
  cv2.line(frame,(0,l2-int(CUR_S)),(width,l2-int(CUR_S)),(0,0,0),1)
  cv2.line(frame,(pipe,0),(pipe,height),(0,255,0),1)
  
  cv2.line(frame,(0,l2+2),(width,l2+2),(0,0,255),1)
  cv2.line(frame,(0,l4+2),(width,l4+2),(0,0,255),1)
  
  cv2.line(frame,(la,0),(la,height),(0,0,255),1)
  cv2.line(frame,(lb,0),(lb,height),(0,0,255),1)
  
  cv2.imshow('frame',frame)
  
#  if STOP:
#    time.sleep(10000)


def bird_pos(frame, w, l):
  bird_top_pos = 0
  bird_buttom_pos = 0
  no_bird = True
  
  for i in range(la, lb):
    r = frame.item(l,i,2)
    g = frame.item(l,i,1)
    b = frame.item(l,i,0)
    v = b + b - r - g - 1
    
    if i > la - 10 and i < lb - 10:
      if v < 20:
        bird_top_pos = i
      else:
        bird_buttom_pos = i
        if i - bird_top_pos < 50 and i - bird_top_pos > 0:
          break
          pass
          
  return bird_top_pos

def pipe_pos(frame, w, l):
  top_pipe_pos = -1
  blue_count = 0
  
  for i in range(la+60, lb-80):
    r = frame.item(l,i,2)
    g = frame.item(l,i,1)
    b = frame.item(l,i,0)
    v = b + b - r - g
    
#    print "%d,%d,%d"%(r,g,b)
    if v > 10 or (r > 200 and g > 200 and b > 200):
      blue_count += 1
#      print blue_count
      if blue_count == 1 :
        top_pipe_pos = i
        
    else:
      if blue_count > H2_1 - 20.0 and blue_count < H2_1 + 20.0:
        return top_pipe_pos
      blue_count = 0
        
  return -1

xxx = 111

h0 = 0.0
t0 = 0.0
H0 = 235.0
def calc_b(t):
  global h0
  global t0
  global BIRD
  
  delta_t = t - t0
  
  if len(pipe_queue):
    p = pipe_queue[0]
    s = Sb - (time.time() - p['t'])*V
  else :
    s = 9
    
#  if s < 0:
#    g = 600
#  else :
  g = G
  
  if delta_t < Tj:
#    print '*1',h0 , delta_t , Tj , J
    b = h0 + delta_t / Tj * J
  else:
#    print '*2'
    b = h0 + J - 0.5 * g * (delta_t - Tj) ** 2
  
  BIRD = b
  print 'b:',b, t
  return b
  
V = 204.0
Tj = 0.30
J = 70.0 # 0.5 * G * (Tj**2)#71.0
G = 2.0* J/ ((0.595-Tj)**2)
print G
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

BIRD = 0
PIPE = 0
SURVIVE = 0
CUR_S = 0

def jump(b):
  global h0
  global t0
  global ser
  
  print "jumpppppppppppp", time.time()
#  if STOP:
#    time.sleep(10000)
    
  
  t0 = time.time()
  h0 = b
  
#  ser.write("\n")
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
  global pipe_queue
  global PIPE
  global SURVIVE
  global CUR_S
  global STOP
  now = time.time()
    
  if len(pipe_queue) > 0:
    p = pipe_queue[0]
    h1 = p['h1']
    s = Sb - (now - p['t'])*V
    CUR_S = s
  else:
    h1 = -1
  
  if h1 < 0:
#    print '=1'
    if b <= B0:
      jump(b)
      
  elif s > 0:
    print '=2',b,h1,s,K
    PIPE = h1
    SURVIVE = h1 - s*K + Bp
    if (h1 - b)/K < s + Bd  or  b <= B0:
      jump(b)
  
  elif L - 10 +s >= 0:
    print '=3'
    SURVIVE = Bp + h1
    if b < Bp + h1:
      jump(b)
  
  else:
    print '=4'
    STOP = True
    pipe_queue = pipe_queue[1:]


if __name__ == '__main__2':
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
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
#      cv2.imwrite("shot.png", frame)
      break

  cap.release()
  cv2.destroyAllWindows()
  exit(0)


#time.sleep(3)
#ser.write("\n")
#time.sleep(0.33)
#ser.write("\n")
#time.sleep(0.33)
#ser.write("\n")
#time.sleep(0.80)
#ser.write("\n")
  

if __name__ == '__main__':
  thread.start_new_thread(video_thread,())
  time.sleep(5)
  
  h0 = H0
  jump(H0)
  
  while True:
    t = time.time()
    
    b = calc_b(t)
    action(b)
    time.sleep(0.01)

time.sleep(2)

