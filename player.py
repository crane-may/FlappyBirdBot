from Tkinter import * 
from PIL import Image, ImageTk, ImageDraw
import os, time, thread
import draw

class LogLine():
  pass
  
class Player():
  def __init__(self, drawFunc):
    self.logs = []
    for l in open('data/log'):
      arr = l.strip().split(' ')
      if len(arr) > 2:
        logline = LogLine()
        logline.time = float(arr[0])
        for i in range(1,len(arr),2):
          setattr(logline,arr[i], float(arr[i+1]))
        self.logs.append(logline)
    
    self.files = []
    for f in os.listdir("data"):
      if f.endswith('jpg'):
        self.files.append(f)
        
    self.files.sort()
    
    self.start_time = float(self.files[0].replace('.jpg',''))  
    self.last_img = None
    self.playing = False
    self.playing_stop = False

    self.top=Tk()
    self.top.geometry('670x600')

    self.label=Label(self.top,text='',font='Helvetica -12')

    self.can = Canvas(self.top)
    self.can.pack()
    self.can.config(width=670, height=500)
    
    for i in range(0,481,50):
      self.can.create_line(640, i, 670, i)
      self.can.create_text((655, i+9),text=str(i))
    
    for i in range(0,640,50):
      self.can.create_line(i, 480, i, 500)
      self.can.create_text((i+15, 490),text=str(i))
    
    self.label.pack()
    self.scale=Scale(self.top,from_=0,to=len(self.files)-1,orient=HORIZONTAL,command=self.resize)
    self.scale.set(0)
    self.scale.pack(fill=X)
    self.playBtn = Button(self.top,text='Play',command=self.play)
    self.playBtn.pack()
    
    self.top.bind("<Right>", self.next)
    self.top.bind("<Left>", self.prev)
    self.top.bind("<space>", lambda event: self.play())
    self.top.bind("<q>", lambda event: self.top.quit())
    
    self.drawFunc = drawFunc
    
    mainloop()
    
  def getTime(self,n):
    cur = float(self.files[n].replace('.jpg',''))
    return cur - self.start_time

  def getImg(self,n):
    image = Image.open("data/%s" % self.files[n])
    
    time = self.getTime(n)
    for l in self.logs:
      if l.time - self.start_time > time:
        self.label.config(text="video: %f, data: %f"%(time, l.time-self.start_time))
        self.drawFunc(image, l)
        break
    
    self.photo = ImageTk.PhotoImage(image)
    return self.photo

  def showImg(self,n):
#    print n
    img = self.can.create_image(0, 0, image=self.getImg(n), anchor=NW)
    if self.last_img:
      self.can.delete(self.last_img)
    self.last_img = img
  
  def resize(self, ev=None):
    self.showImg(self.scale.get())

  def play_thread(self):
    next_index = self.scale.get()
    play_start = time.time() - self.getTime(next_index)
  
    self.playing = True
    self.playing_stop = False
  
    while True:
      now = time.time()
      if now - play_start > self.getTime(next_index):
        self.scale.set(next_index)
        next_index += 1
    
      if next_index >= len(self.files) or self.playing_stop:
        self.playing = False
        break
      time.sleep(0.01)

  def play(self):
    if self.playing:
      self.playing_stop = True
      self.playBtn.config(text='Play')
    else:
      thread.start_new_thread(self.play_thread,())
      self.playBtn.config(text='Pause')
  
  def next(self,e):
    next_index = self.scale.get() + 1
    if next_index < len(self.files):
      self.scale.set(next_index)
  def prev(self,e):
    prev_index = self.scale.get() - 1
    if prev_index > 0:
      self.scale.set(prev_index)


def drawLog(im, data):
  img = draw.start(im)
  draw.line(img, (0, 300), (640, 300), (255,0,0))
  draw.point(img, (data.b,300))
  draw.end(img)

if __name__ == '__main__':
  p = Player(drawLog)

