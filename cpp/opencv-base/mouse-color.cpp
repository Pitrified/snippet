#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <iostream>

using namespace cv;
using namespace std;

// compile with this
// g++ img-display.cpp -o img-display `pkg-config --cflags --libs opencv`
//
void OnMouseChangeColor(int event, int x, int y, int flags, void *userdata) {
    if (event != EVENT_LBUTTONDOWN)
        return;

    cout << "Left button pressed (" << x << "," << y << ")" << endl;

    // continuano i magheggi: casto userdata in un punto
    // ora posso accedere ai campi di Point
    Point *punto = (Point*) userdata;
    punto->x = x;
    punto->y = y;
}

int main( int argc, char** argv ) {
    string imgName;
    if( argc != 2) {
        imgName = "sample.png";
        cout <<"Usage: ./mouse-color.out ImageToLoadAndDisplay" << endl;
        cout <<"imgName set as " << imgName << endl;
    }
    else {
        imgName = argv[1];
    }

    Mat image;
    image = imread(imgName, CV_LOAD_IMAGE_COLOR);   // Read the file

    if(! image.data ) {                             // Check for invalid input
        cout << "Could not open or find the image" << endl ;
        return -1;
    }

    string windowName = "Display window";
    namedWindow(windowName, WINDOW_AUTOSIZE );// Create a window for display

    imshow(windowName, image);                // Show our image inside it
    // setMouseCallback(windowName, OnMouseChangeColor, NULL);
    Point erpunto;
    // faccio magheggi, passo il punto per referenza
    // ma lo casto a void direi cosi` il callback e` contento
    setMouseCallback(windowName, OnMouseChangeColor, (void*)&erpunto);

    int k = -1;
    while (1) {
        k = waitKey(1000);             // Wait for a keystroke in the window
        // cout << k << endl;
        if (k != 255)
            break;
        cout << "erpunto (" << erpunto.x << "," << erpunto.y << ")" << endl;
    }
    return 0;
}

