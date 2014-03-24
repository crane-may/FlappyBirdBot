#include "highgui.h"
#include <iostream>
#include <vector>
#include <stdio.h>

using namespace cv;
using namespace std;

//hide the local functions in an anon namespace
namespace 
{
    int process(VideoCapture& capture) 
   {
      int n = 0;
        char filename[200];
        string window_name = "video | q or esc to quit";
        cout << "press space to save a picture. q or esc to quit" << endl;
        
        namedWindow(window_name, CV_WINDOW_KEEPRATIO); //resizable window;
        
  
			  int fps=0;
			  time_t last_t=0;
			  time_t now;
				
        Mat frame, frameCopy;        
        int i =0;
        for (;;) 
        {

			    fps++;
			    time(&now);
					
					if (now > last_t){
            cout << fps << endl;
			      fps = 0;
			    }
			    last_t = now;
					
					
            capture >> frame;
            // cout << (i++) << endl;
            if (frame.empty())
                break;
            
            // imshow(window_name, frame);
            // char key = (char)waitKey(5); //delay N millis, usually long enough to display and capture input
            // 
            // switch (key) 
            // {
            // case 'q':
            // case 'Q':
            // case 27: //escape key
            //    return 0;
            //         
            // case ' ': //Save an image
            //    sprintf(filename,"filename%.3d.jpg",n++);
            //    imwrite(filename,frame);
            //    cout << "Saved " << filename << endl;
            //    break;
            //         
            // default:
            //    break;
            // }
        }
        return 0;
    }

}

int main(int ac, char** av) {

    std::string arg = "0";    
    cout << "Program started..." << endl;
    
    VideoCapture capture(arg); //try to open string, this will attempt to open it as a video file
    
    if (!capture.isOpened()) //if this fails, try to open as a video camera, through the use of an integer param
        capture.open(atoi(arg.c_str()));
    
    if (!capture.isOpened()) {
        cerr << "Failed to open a video device or video file!\n" << endl;        
        return 1;
    }
   
    return process(capture);
}
