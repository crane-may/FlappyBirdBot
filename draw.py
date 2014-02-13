import numpy as np
import cv2
from PIL import Image, ImageTk, ImageDraw

def c(color):
  return (color[2],color[1],color[0])

def start(img):
  if isinstance(img, Image.Image):
    return ImageDraw.Draw(img)
  else:
    return img

def end(img):
  if isinstance(img, ImageDraw.ImageDraw):
    del img

def line(img, start, end, color=(0,0,0), width=3):
  if isinstance(img, ImageDraw.ImageDraw):
    img.line(start + end, fill=color, width=width)
  else:
    cv2.line(img, start, end, c(color), width)
    
def point(img, pos, color=(0,0,0), r=4):
  if isinstance(img, ImageDraw.ImageDraw):
    img.ellipse((pos[0]-r, pos[1]-r, pos[0]+r, pos[1]+r), fill=color)
  else:
    cv2.circle(img,pos,r/2,c(color),r)
    
def box(img, p1, p2, color=(0,0,0), width=3):
  if isinstance(img, ImageDraw.ImageDraw):
    img.rectangle(p1+p2, fill=color,width=3)
  else:
    cv2.rectangle(img,p1,p2,c(color),width)
