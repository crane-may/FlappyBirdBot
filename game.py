import numpy as np
import cv2, time, thread, serial, thread, draw, sys, player, viewcolor
from bird import bird


class game:
    def __init__(self):
        self.left = 60 # 系统测量
        self.top = 20 # 系统测量
        self.right = 460 # 系统测量
        self.buttom = 420 # 系统测量
        self.bird_line_y = self.top + 300 # 系统测量
        self.pipe_width = 80 # 系统测量
        self.pipe_v = 225.0 # 系统测量
        
        self.pipe_queue = []
        self.bird = bird()
        self.detect_screen(frame)
        self.detect_bird(frame)
        self.pipe_line_y = self.top + self.pipe_width + 10
        self.pipe_line_on = False
        self.start_t = time.time()
        self.last_calc_t = self.start_t
        self.last_calc_bird_x = self.bird.x
        self.calc_t_interv = self.bird.jump_t

    def detect_pipe(frame):
        pipe_top_avg = 0
        pipe_y = self.pipe_line_y
        for i in range(self.left + 10, self.left + 40): # 10 和 40 是经验值 
            r = frame.item(self.pipe_line_y,i,2)
            g = frame.item(self.pipe_line_y,i,1)
            b = frame.item(self.pipe_line_y,i,0)
            pipe_top_avg += b + b - r - g - 1

        if self.pipe_line_on and pipe_top_avg > 0:
            self.pipe_line_on = False
        elif (not self.pipe_line_on) and pipe_top_avg < 0:
            pipe_y_on = False
            for j in range(self.pipe_line_y - self.pipe_width - 5, self.pipe_line_y + self.pipe_width + 5):
                r = frame.item(j,self.left + 25,2)  # 10 和 40 的中值
                g = frame.item(j,self.left + 25,1)
                b = frame.item(j,self.left + 25,0)
                v = b + b - r - g - 5
                if v < 0 and (not pipe_y_on):
                    pipe_y = j
                    pipe_y_on = True
                elif pipe_y_on:
                    print "pipe_width : ", j - pipe_y
                else:
                    pass


            for i in range(self.left + 40, self.right): # 和上面的 40 相对应
                r = frame.item(self.pipe_line_y,i,2)
                g = frame.item(self.pipe_line_y,i,1)
                b = frame.item(self.pipe_line_y,i,0)
                v = b + b - r - g - 5
                if v > 0:
                    pipe_t = time.time() + (self.bird_line_y - pipe_y) / self.pipe_v
                    self.pipe_queue.append({"x": i + self.pipe_space, "t": pipe_t})
                    self.pipe_line_on = True
        else:
            return

    def calculate_bird_jump():
        if len(self.pipe_queue[0]) > 0:
            next_pipe = self.pipe_queue[0]
            bird_pipe_delta_x = next_pipe["x"] - self.last_calc_bird_x + 10  # 10 是经验值 
            if bird_pipe_delta_x > 0:
                up_jump_times = int(bird_pipe_delta_x / self.bird.jump_height)
                next_jump_t = self.last_calc_t 
                for i in range(1, up_jump_times):
                    next_jump_t += self.bird.jump_up_t
                    self.bird.jump_queue.append(next_jump_t)
                self.last_calc_bird_x += up_jump_times * self.bird.jump_height
            else:
                next_jump_t = self.bird.jump_down_t(bird_pipe_delta_x * (-1))
                self.bird.jump_queue.append(next_jump_t)
                self.last_calc_bird_x -= bird_pipe_delta_x

            flat_jump_times = int((next_pipe["t"] + (self.pipe_width / self.pipe_v) - next_jump_t) / self.bird.jump_t)
            for i in range(1, flat_jump_times):
                next_jump_t += self.bird.jump_t
                self.bird.jump_queue.append(next_jump_t)
            self.last_calc_t = next_jump_t

        else:
            next_jump_time = time.time() + self.calc_t_interv
            if next_jump_time > self.last_calc_t:
                self.bird.jump_queue.append(next_jump_time)
                self.last_calc_t = next_jump_time


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

def run():
  global h0,LOGFILE
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

def replay():
  p = player.Player(drawFunc, lb, l2, 0.3)

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print 'usage: python bird2.py [run|picture|replay|correct]' 
  else:
    eval("%s()"%sys.argv[1])
    
