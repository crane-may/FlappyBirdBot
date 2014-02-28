from Tkinter import * 
from PIL import Image, ImageTk, ImageDraw
import os, time, thread, re, copy
import draw, math, detect, core, cv2

class LogLine():
  pass
  
class Player():
  def __init__(self, zeroX, zeroY, path='datalog'):
    self.zeroX = zeroX
    self.zeroY = zeroY+2
    self.path = path
    
    self.files = []
    for f in os.listdir(path):
      if f.endswith('jpg'):
        self.files.append(f)
    
    self.top=Tk()
    self.top.geometry('670x600')

    self.can = Canvas(self.top)
    self.can.pack()
    self.can.config(width=670, height=500)
    
    for i in range(-450,450,50):
      self.can.create_line(640, i+self.zeroY, 670, i+self.zeroY)
      self.can.create_text((655, i+self.zeroY+9),text=str(abs(i)))
    
    for i in range(-650,640,50):
      self.can.create_line(i+self.zeroX, 480, i+self.zeroX, 500)
      self.can.create_text((i+self.zeroX+15, 490),text=str(abs(i)))

    self.label=Label(self.top,text='',font='Helvetica -12')    
    self.label.pack()
    self.label2=Label(self.top,text='',font='Helvetica -12')    
    self.label2.pack()
    self.scale=Scale(self.top,from_=0,to=len(self.files)-1,orient=HORIZONTAL,command=self.resize)
    self.scale.set(0)
    self.scale.pack(fill=X)
    
    self.top.bind("<Right>", self.next)
    self.top.bind("<Left>", self.prev)
    self.top.bind("<Down>", self.next10)
    self.top.bind("<Up>", self.prev10)
    self.top.bind("<q>", lambda event: self.top.quit())
    self.top.bind("<Motion>", self.mouseMove)
    self.top.bind("<space>", self.to600)
    
    self.last_img = None
    mainloop()
    
  def getImg(self,n):
    image = Image.open(self.path+"/%s" % self.files[n])
    
    frame = cv2.imread(self.path+"/%s" % self.files[n])
    b = core.GROUND_X - detect.bird_h(frame, core.DETECT_BIRD_Y, core.GROUND_X, core.PIPE_SPACE)
    
    draw = ImageDraw.Draw(image)
    r = 4
    draw.line((0,core.DETECT_BIRD_Y,640,core.DETECT_BIRD_Y),fill='#000',width=1)
    draw.ellipse((b-r, core.DETECT_BIRD_Y-r, b+r, core.DETECT_BIRD_Y+r), fill='#0ff')
    del draw
    self.photo = ImageTk.PhotoImage(image)
    return self.photo

  def showImg(self,n):
    print self.files[n]
    img = self.can.create_image(0, 0, image=self.getImg(n), anchor=NW)
    if self.last_img:
      self.can.delete(self.last_img)
    self.last_img = img
    
  
  def resize(self, ev=None):
    self.showImg(self.scale.get())
  
  def next(self,e):
    next_index = self.scale.get() + 1
    if next_index < len(self.files):
      self.scale.set(next_index)
  def prev(self,e):
    prev_index = self.scale.get() - 1
    if prev_index >= 0:
      self.scale.set(prev_index)
  
  def next10(self,e):
    next_index = self.scale.get() + 10
    if next_index < len(self.files):
      self.scale.set(next_index)
  def prev10(self,e):
    prev_index = self.scale.get() - 10
    if prev_index >= 0:
      self.scale.set(prev_index)
      
  def to600(self,e):
    if 700 <len(self.files):
      self.scale.set(700)
  
  def mouseMove(self, event):
    self.mouse_x = event.x
    self.mouse_y = event.y
    self.label2.config(text="x: %f, y: %f"%(abs(event.x-self.zeroX), abs(event.y-self.zeroY)))

if __name__ == '__main__':
  if len(sys.argv) == 2:
    p = Player(600,323,sys.argv[1])
  else:
    p = Player(600,323)


