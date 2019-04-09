#include <iostream>
#include <vector>
#include <opencv2/opencv.hpp>

#include <waver.h>

using namespace cv;
using namespace std;

int main(int argc, char** argv)
{
    // int width = 200;
    int width = 900;
    // int heigth = 100;
    int heigth = 600;
    string winName = "Onde";

    // Waver wavez (width, heigth, winName);
    Waver wavez (width, heigth);
    wavez.setWinName(winName);

    // wavez.showFrame(10);

    // wavez.tester();
    wavez.film();

    // waitKey(0);
}
