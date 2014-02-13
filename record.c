#include <cv.h>
#include <highgui.h>
#include <stdio.h>

void main(int argc,char *argv[])
{ 
  int c;
  IplImage* color_img;
  CvCapture* cv_cap = cvCaptureFromCAM(0);
/*  cvSetCaptureProperty(pCapture, CV_CAP_PROP_FPS, 15);*/
/*  cvSetCaptureProperty(pCapture, CV_CAP_PROP_FRAME_WIDTH, 320); */
/*  cvSetCaptureProperty(pCapture, CV_CAP_PROP_FRAME_HEIGHT, 240);*/
/*  cvNamedWindow("Video",CV_WINDOW_AUTOSIZE); // create window*/
  
  int fps=0;
  time_t last_t=0;
  time_t now;
  
  for(;;) {
    fps++;
    time(&now);
    
    if (now > last_t){
      printf("%d\n", fps);
      fps = 0;
    }
    last_t = now;
    
    color_img = cvQueryFrame(cv_cap); // get frame
    
/*    if(color_img != 0)*/
/*      cvShowImage("Video", color_img); // show frame*/
/*    c = cvWaitKey(10); // wait 10 ms or for key stroke*/
/*    if(c == 27)*/
/*      break; */
  }
  cvReleaseCapture( &cv_cap );
  cvDestroyWindow("Video");
}
