

file = None

def w(s):
  global file
  file.write('%s\n'%s)

def start():
  global file
  file = open('color.html','w')
  w('<!DOCTYPE html>')
  w('<html>')
  w('<head>')
  w('<style>')
  w('div{height:15px;width:100%;line-height:15px;margin:0;padding:0}')
  w('</style>')
  w('</head>')
  w('<body>')
  
def end():
  global file
  w('</body>')
  w('</html>')
  file.close()
  file = None

index = 0
def setIndex(i):
  global index
  index = i

def rgb(r,g,b):
  global index
  if file == None:
    return
  index += 1
  w("<div style='background-color:rgb(%d,%d,%d)'>%d&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;%d,%d,%d</div>"%(r,g,b,index,r,g,b))
