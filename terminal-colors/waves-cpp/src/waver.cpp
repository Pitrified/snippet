#include <iostream>
#include <limits.h>
#include <chrono>
#include <thread>
#include <cmath>

#include <opencv2/core.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>

#include <waver.h>

using namespace cv;
using namespace std;

Waver::Waver(int _width, int _heigth)
  // :  frame ( heigth, width, CV_8UC3, Scalar(0,0,0) )
{
    width = _width;
    heigth = _heigth;
    int hue_max = 180;
    Scalar baseValue = Scalar(hue_max*4/6, 255, 255);
    frame = Mat( heigth, width, CV_8UC3, baseValue);

    film_end = 100;

    // funcMin = 0;
    // funcMax = 150;
    calcMinMax();
}

void Waver::calcMinMax() {
    funcMin = INT_MAX;
    funcMax = INT_MIN;
    // int max_t = 100;
    int max_t = film_end;
    for (int x=0; x < width; x++) {
        for (int y=0; y < heigth; y++) {
            for (int t=0; t < max_t; t++) {
                double z = wave1(x, y, t);
                // cout << "z " << z << " funcMin " << funcMin << " funcMax " << funcMax << endl;
                if (z < funcMin) {
                    // cout << "z " << z << " funcMin " << funcMin << endl;
                    funcMin = (int) floor(z);
                }
                if (z > funcMax) {
                    // cout << "z " << z << " funcMax " << funcMax << endl;
                    funcMax = (int) ceil(z);
                }
            }
        }
    }
    cout << "funcMin " << funcMin << " funcMax " << funcMax << endl;
}

Waver::Waver(int _width, int _heigth, string _winName)
    : Waver(_width, _heigth) {
    winName = _winName;
}

void Waver::showFrame(int t) {
    // cout << "Show size " << frame.size() << endl;
    // cout << "winName '" << winName << "'" << endl;
    // cout << "width " << width << " heigth " << heigth << endl;
    evaluate(t);
    Mat frame_rgb;
    cvtColor(frame, frame_rgb, CV_HSV2BGR);
    // cvtColor(frame, frame_rgb, CV_HSV2RGB);
    // imshow(winName, frame);
    imshow(winName, frame_rgb);
    waitKey(1);
}

double sinc(double x) {
    if (x==0)
        return 1;
    return sin(x)/x;
}

double Waver::wave1(int x, int y, int t) {
    double theta = atan2(x, y);
    double rho = sqrt(pow(x,2) + pow(y,2));
    double rho_c = sqrt( pow((x-width/2),2) + pow((y-heigth/2),2));
    double rho_l = sqrt( pow((x+width/2),2) + pow((y-heigth/2),2));

    // double z = ( x + y)  * sin(t * M_PI / 12);

    // double z = 10 * sin(t * M_PI / 16) * sinc(0.1 * (x-width/2) ) * sinc(0.1 * (y-heigth/2) ); // sinc translated

    // double z = 10 * sin( - rho * t * M_PI / 12 ); // weird effects
    
    double z =  10;
    z *= sin(rho_l/16 - t * M_PI / 12);
    z *= sin(rho_l/24 - t * M_PI / 10);
    z *= sin(rho_l/40 - t * M_PI / 8); // # decent waves !!!

    // double z =  10 * sin( rho_c/9);
    // z *= sin( - t * M_PI / 12 );
    // z *= sin( - t * M_PI / 18 );

    // #  return 10 * sin( rho/3 - t * pi / 12 ) * sin ( rho/8 - t * pi / 8 ) # decent waves !!!
    
    // cout << "z " << z << endl;
    return z;
}

void Waver::evaluate(int t) {
    MatIterator_<Vec3b> it, end;
    int x = 0;
    int y = 0;
    for( it = frame.begin<Vec3b>(), end = frame.end<Vec3b>(); it != end; ++it)
    {
        // double z = (int) wave1(x, y, t);
        double z = wave1(x, y, t);

        if (z < funcMin) {
            cout << "Minimo errato z " << z << " funcMin " << funcMin << endl;
            // funcMin = (int) floor(z);
        }
        if (z > funcMax) {
            cout << "Massimo errato z " << z << " funcMax " << funcMax << endl;
            // funcMax = (int) ceil(z);
        }


        // cout << "z " << z << endl;
        int sat = (int) ((z-funcMin)/(funcMax-funcMin) * 255);
        (*it)[1] = sat;
        // cout << "x " << x << " y " << y << " s " << sat << endl;
        x++;
        if (x == width) {
            x=0;
            y++;
        }
    }

    // for (int x=0; x < width; x++) {
        // for (int y=0; y < heigth; y++) {
            // double z = wave1(x, y, t);
            // int sat = (int) ((z-funcMin)/(funcMax-funcMin) * 255);
            // frame.at<Vec3b>(y, x)[1] = sat;
        // }
    // }
}

void Waver::film() {
    int x = 100;
    for (int i=0; i<film_end; i++) {
        showFrame(i);
        std::this_thread::sleep_for(std::chrono::milliseconds(x));
    }
}

void Waver::tester() {
    int width = 3;
    int heigth = 3;

    Scalar baseValue = Scalar(0, 255, 255);
    Mat frame_test = Mat( heigth, width, CV_8UC3, baseValue);
    cout << "frame\n" << frame_test << endl;

    MatIterator_<Vec3b> it, end;
    int x = 0;
    int y = 0;
    int t = 10;

    funcMin = 0;
    funcMax = 10;

    for(it=frame_test.begin<Vec3b>(),
        end=frame_test.end<Vec3b>();
        it!=end; ++it)
    {
        // double z = (int) wave1(x, y, t);
        double z = wave1(x, y, t);
        // cout << "z " << z << endl;
        int sat = (int) ((z-funcMin)/(funcMax-funcMin) * 255);
        (*it)[1] = sat;
        // cout << "x " << x << " y " << y << " s " << sat << endl;
        x++;
        if (x == width) {
            x=0;
            y++;
        }
    }

    cout << "frame dopo HSV\n" << frame_test << endl;

    Mat frame_rgb_test;
    cvtColor(frame, frame_rgb_test, CV_HSV2BGR);
    // imshow(winName, frame);
}

