from Tkinter import * 
from PIL import Image, ImageTk, ImageDraw
import os, time, thread, re, copy
import draw, math

class LogLine():
  pass
  
class Player():
  def __init__(self, zeroX, zeroY, path='datalog'):
    self.zeroX = zeroX
    self.zeroY = zeroY+2
    self.path = path
    
    expr =  '([0-9.]+);'+\
            '(\[\w+\])?'+\
            '(<[^>]+>)?'+\
            '(L\(([0-9.]+),([0-9.]+),([0-9.]+),([0-9.]+)(#\w+)?\))?'+\
            '(P\(([0-9.]+),([0-9.]+)(#\w+)?\))?'+\
            '(\{[^}]+\})?'
    
    
    logs = []
    if os.path.exists(path+'/log'):
      for l in open(path+'/log'):
        logs.append(l)
        
    logs.sort()
    
    self.start = -1
    self.graphs = []
    hold_graph = {}
    for l in logs:
      ma = re.match(expr, l)
      if ma:
        ll = ma.groups()
        t = float(ll[0])
        holder = ll[1]
        
        cur = int(t*100)
        if self.start < 0:
          self.start = cur
          print self.start
          
        idx = cur - self.start
        while idx >= len(self.graphs):
          self.graphs.append(copy.deepcopy(hold_graph))
        
        if holder:
          self.graphs[idx][holder] = ll
          hold_graph[holder] = ll
        else:
          if not self.graphs[idx].has_key('_'):
            self.graphs[idx]['_'] = []
          self.graphs[idx]['_'].append(ll)
    
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
    self.scale=Scale(self.top,from_=0,to=len(self.graphs)-1,orient=HORIZONTAL,command=self.resize)
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
    
  def showImg(self,n):
    self.label.config(text="%f, %f"%(n/100.0, (self.start + n) /100.0))
    print '-------------- :%d'%n
    
    graph = self.graphs[n]
    if graph.has_key('[B]'):
      print graph['[B]'][2]
      filename = graph['[B]'][2].strip('<>')
      image = Image.open(self.path+"/%s" % filename)
      
      ####
      
      gs = []
      for (k,v) in graph.items():
        if k == '[B]':
          continue
        elif k == '_':
          gs += graph[k]
        else:
          gs.append(graph[k])
      
      draw = ImageDraw.Draw(image)
      for g in gs:
        (t, holder, jpg, L, lx1, ly1, lx2, ly2, lcolor, P, px, py, pcolor, out) = g
        if L:
          if lcolor == None:
            lcolor = '#000'
          draw.line((float(lx1), float(ly1), float(lx2), float(ly2)), fill=lcolor, width=1)
        elif P:
          if pcolor == None:
            pcolor = '#000'
          draw.ellipse((float(px)-4, float(py)-4, float(px)+4, float(py)+4), fill=pcolor)
        elif out:
          print t,out
        
      del draw
      
      ####
      
      self.photo = ImageTk.PhotoImage(image)
      img = self.can.create_image(0, 0, image=self.photo, anchor=NW)
    else:
      img = None
      
    if self.last_img:
      self.can.delete(self.last_img)
    self.last_img = img
  
  def resize(self, ev=None):
    self.showImg(self.scale.get())
  
  def next(self,e):
    next_index = self.scale.get() + 1
    if next_index < len(self.graphs):
      self.scale.set(next_index)
  def prev(self,e):
    prev_index = self.scale.get() - 1
    if prev_index >= 0:
      self.scale.set(prev_index)
  
  def next10(self,e):
    next_index = self.scale.get() + 10
    if next_index < len(self.graphs):
      self.scale.set(next_index)
  def prev10(self,e):
    prev_index = self.scale.get() - 10
    if prev_index >= 0:
      self.scale.set(prev_index)
      
  def to600(self,e):
    if 700 <len(self.graphs):
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


