import numpy as np
import cv2, sys, time, os

class Diff:
  def __init__(self, v1, v2):
    self.v1 = v1
    self.v2 = v2
    self.i_avg_f =  np.zeros((480,640,1), np.float32)
    self.i_diff_f = np.zeros((480,640,1), np.float32)
    self.i_prev_f = None
    self.i_hi_f =   None
    self.i_low_f =  None
    self.i_cnt = 0.0

  def acc_back(self, frame):
    if self.i_prev_f != None:
      cv2.accumulate(frame, self.i_avg_f)
      diff = cv2.absdiff(frame, self.i_prev_f)
      cv2.accumulate(diff, self.i_diff_f)
      self.i_cnt += 1
    
    self.i_prev_f = frame.copy()
  
  def create_models_from_stats(self):
    self.i_avg_f = self.i_avg_f / self.i_cnt
    self.i_diff_f = (self.i_diff_f / self.i_cnt) + 1.0
    self.setHighThreshold(self.v1)
    self.setLowThreshold(self.v2)

  def setHighThreshold(self, scale):
    self.i_hi_f = self.i_diff_f * scale + self.i_avg_f
  
  def setLowThreshold(self, scale):
    self.i_low_f = self.i_avg_f - self.i_diff_f * scale
  
  def background_diff(self, frame):
    i_mask = cv2.inRange(frame, cv2.convertScaleAbs(self.i_low_f), cv2.convertScaleAbs(self.i_hi_f))
    i_mask = 255 - i_mask
    return i_mask