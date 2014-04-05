import numpy as np
import cv2, time, serial, thread, draw, sys, player, viewcolor, sys, os, json, colorsys, detect_backdiff

ser= None

######################

HIGHT = 480.0
WIDTH = 640.0
DECIDE_FREQ = 0.005
MIN_JUMP_FREQ = 0.10
TAP_DELAY = 0.055
MAX_CORRECT_H = 15

B_START_H = 258.0
B_JUMP_H = 82.0
B_JUMP_UP_T = 0.29605
B_WIDTH = 40.0
B_Y = 323
PIPE_V = 219.0
PIPE_W = 95.0
PIPE_SPACE = 174.0
PIPES_GAP = 240.0
SURV_PIPE_H = 24.0
SURV_PIPE_W = 7.5
SURV_H = 70.0
SURV_K = 1.0
GROUND_X = 600.0
DETECT_PIPE_Y = 80
DETECT_PIPE_TOP_X = 15
DETECT_BIRD_Y = 345
DETECT_TIMER_X = 622


game_start = False
correct_start = False
last_jump_h = 0
last_jump_t = 0
last_correct_b_t = 0
pipe_queue = []
b_h_history = []

log = None
######################

def calc_bird_h(t):
  global last_jump_h, last_jump_t, b_h_history
  delta_t = t - last_jump_t
  
  b_h = 1000.0*(0.3404*delta_t**3-1.3753*delta_t**2+0.6947*delta_t) + last_jump_h
  # b_h = 1000*(0.3396*delta_t**3-1.3575*delta_t**2+0.6636*delta_t+0.0056) + last_jump_h
  # b_h = last_jump_h + B_JUMP_H*(1 - (delta_t - B_JUMP_UP_T)**2/B_JUMP_UP_T**2)
  # b_h -= calc_b_h_addon(delta_t)
  
  b_h_history.append((t,b_h,delta_t))
  if b_h_history[0][0] + 0.25 < t:
    b_h_history = b_h_history[1:]
  
  return b_h

def calc_b_h_addon(delta_t):
  if delta_t > 0.55:
    d = 46.5 * delta_t**2 - 69.15 * delta_t + 25.83
    if delta_t > 0.834:
      d += -0.4 * delta_t**2 + 6.232 * delta_t -2.415264 
    return d
  else:
    return 0

def calc_survival_h(t):
  global pipe_queue
  
  if len(pipe_queue) > 0:
    next_pipe = pipe_queue[0]
  else:
    return SURV_H
    
  b_to_pipe_dist = B_Y - DETECT_PIPE_Y - (t - next_pipe["t"]) * PIPE_V
  pipe_surv_h = next_pipe["h"] + SURV_PIPE_H
  close_pipe_dist = (pipe_surv_h - SURV_H) / SURV_K + SURV_PIPE_W
  
  log_w(t, "[PX]L(%f,%f,%f,%f#00f)"%(GROUND_X-next_pipe["h"], B_Y - b_to_pipe_dist, GROUND_X-next_pipe["h"], B_Y - b_to_pipe_dist - PIPE_W - B_WIDTH))
  log_w(t, "[PY]L(%f,%f,%f,%f#00f)"%(GROUND_X-next_pipe["h"], B_Y - b_to_pipe_dist, GROUND_X, B_Y - b_to_pipe_dist))
  
  if b_to_pipe_dist > close_pipe_dist:
    return SURV_H
  elif b_to_pipe_dist > 0:
    # return (close_pipe_dist - b_to_pipe_dist) * SURV_K + SURV_H
    s = abs(b_to_pipe_dist - 0.6*PIPE_V)
    if s < 50.0 and next_pipe["h"] > 300.0:
      pipe_surv_h -= 100.0
      log_w(t, "{limited adjust}")
      
    return pipe_surv_h
    
  elif b_to_pipe_dist > -1.0 * (PIPE_W + B_WIDTH):
    # if abs((t - last_jump_t) * PIPE_V + b_to_pipe_dist) < 10.0:
    #   pipe_surv_h += 30
    #   log_w(t, "{extra adjust}")
    if t - last_jump_t > 0.7:
      log_w(t, "{fast adjust}")
      pipe_surv_h += 10.0
    
    return pipe_surv_h
  else:
    log_w(t, "{pipe pop}")
    pipe_queue = pipe_queue[1:]
    return SURV_H
    
  
######################

def append_pipe(frame, frame_delay, now):
  (new_pipe_h, new_pipe_t) = detect_backdiff.pipe_h(frame, PIPE_SPACE, DETECT_PIPE_Y, DETECT_PIPE_TOP_X, GROUND_X, PIPE_W, PIPE_V, frame_delay)
  if new_pipe_h > 0 and (len(pipe_queue) == 0 or now - pipe_queue[-1]['t'] > PIPES_GAP / PIPE_V):
    pipe_queue.append({"h":new_pipe_h, "t":new_pipe_t})
    log_w(now - frame_delay, "{pipe(%d), %f, %f}"%(len(pipe_queue),new_pipe_h, new_pipe_t))

def correct_b_h(frame, frame_delay, now):
  global last_jump_h, last_correct_b_t, last_jump_t
  detect_b_h = detect_backdiff.bird_h(frame, DETECT_BIRD_Y, GROUND_X, PIPE_SPACE)
  log_w(now - frame_delay, "P(%f,%f#0ff)"%(GROUND_X-detect_b_h, DETECT_BIRD_Y))
  
  if len(b_h_history) > 0 and now - last_correct_b_t > frame_delay + 0.03 and correct_start:
    calc_b_h = None
    for h in b_h_history:
      if h[0] >= now - frame_delay:
        calc_b_h = h
        break
        
    if calc_b_h != None:
      delta_t = now - calc_b_h[0]
      if delta_t > 0.05 and delta_t < 0.2:
        b_h_diff = detect_b_h - calc_b_h[1]
        if calc_b_h[2] > 0.55:
          return
        if abs(b_h_diff) > 60:
          return
        if abs(b_h_diff) > MAX_CORRECT_H:
          last_jump_h += b_h_diff / abs(b_h_diff) * MAX_CORRECT_H
        else:
          last_jump_h += b_h_diff
        last_correct_b_t = now
        
        log_w(now, "{add: %f, %f}"%(b_h_diff, MAX_CORRECT_H))
        log_w(now - frame_delay, "{will add: %f, %f}"%(b_h_diff, MAX_CORRECT_H))

######################

def decide_jump_thread():
  global last_jump_h, last_jump_t, game_start, correct_start
  
  time.sleep(4)
  correct_light_timer()
  time.sleep(2)
  
  last_jump_t = time.time()
  last_jump_h = B_START_H
  jump()
  game_start = True
    
  while True:
    t = time.time()
    b_h = calc_bird_h(t)
    surv_h = calc_survival_h(t)
    if b_h < surv_h and t - last_jump_t > MIN_JUMP_FREQ:
      last_jump_h = b_h
      last_jump_t = t
      jump()
      correct_start = True
      log_w(t, "{jumppppppppppppp}")
    
    log_w(t, "[BC]P(%f,%f)"%(GROUND_X - b_h, B_Y))
    log_w(t, "[SUR]L(%f,%f,%f,%f#f00)"%(GROUND_X - surv_h - 100, B_Y - 100, GROUND_X - surv_h + 100, B_Y + 100))
    time.sleep(DECIDE_FREQ)

def calc_fps(fps, last_t):
  fps += 1
  t = int(time.time())
  if t > last_t:
    print fps
    fps = 0
  last_t = t
  
  return fps, last_t
  
def detect_thread():
  cap = cv2.VideoCapture(0)
  cap.set(3,640)
  cap.set(4,480)
  ret, frame = cap.read()
  
  saved_frames = []
  
  fps, last_t = 0, 0
  while(True):
    fps, last_t = calc_fps(fps, last_t)
    
    ret, frame = cap.read()
    now = time.time()
    
    if not game_start:
      continue
    
    frame_delay = detect_backdiff.timer() + TAP_DELAY
    if frame_delay > TAP_DELAY and frame_delay < 0.25:
      frame2 = detect_backdiff.pre_frame(frame)
      append_pipe(frame2, frame_delay, now)
      correct_b_h(frame2, frame_delay, now)
    
      filename = '%f.jpg'%now
      log_w(now-frame_delay, "[B]<%s>"%filename)
      
      filename_full = '/Volumes/RAMDisk/datalog/%s'%filename
      saved_frames.append(filename_full)
      cv2.imwrite(filename_full,frame)
      
      if len(saved_frames) > 5000:
        os.remove(saved_frames.pop(0))
    else:
      log_w(now, "{drop: %f}"%(frame_delay-TAP_DELAY))

  cap.release()

def run():
  global log
  log = open('/Volumes/RAMDisk/datalog/log', 'w')
  now = time.time()
  log_w(now, "[REF_1]L(0,%f,640,%f#ff0)"%(DETECT_PIPE_Y, DETECT_PIPE_Y))
  log_w(now, "[REF_2]L(0,%f,640,%f#ff0)"%(DETECT_BIRD_Y, DETECT_BIRD_Y))
  log_w(now, "[REF_3]L(0,%f,640,%f#ff0)"%(B_Y, B_Y))
  log_w(now, "[REF_4]L(%f,0,%f,480#ff0)"%(DETECT_PIPE_TOP_X, DETECT_PIPE_TOP_X))
  log_w(now, "[REF_5]L(%f,0,%f,480#ff0)"%(GROUND_X, GROUND_X))
  
  thread.start_new_thread(decide_jump_thread,())
  detect_thread()

#####################################

def jump():
  ser.write("\n")

def correct_light_timer():
  tt = int(time.time())
  while True:
    if int(time.time()) > tt:
      ser.write(" ")
      break
    time.sleep(0.001)

def log_w(t, s):
  global log
  log.write("%f;%s\n"%(t, s))
  pass

######################

if __name__ == "__main__":
  ser = serial.Serial("/dev/tty.usbmodem1a1211",19200)
  if len(sys.argv) < 2:
    print 'usage: python bird2.py [run|picture|replay|correct]' 
  else:
    eval("%s()"%sys.argv[1])
