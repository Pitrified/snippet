#ifndef FILTER_H
#define FILTER_H

// #include <iostream>

#include <opencv2/core.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>

using namespace cv;
using namespace std;

class Waver{

public:
    // constructor
    Waver(int width, int heigth);
    Waver(int width, int heigth, string winName);

    // interface
    void showFrame(int t);
    void film();

    // setter - getter
    void setWinName(string _winName) {
        winName = _winName; } ;
    string getWinName() {
        return winName; } ;

    // misc
    void tester();

protected:
    int width;
    int heigth;
    string winName;
    int film_end;

    int funcMin;
    int funcMax;

    Mat frame;

    // double wave1(int t);
    double wave1(int x, int y, int t);
    void evaluate(int t);
    void calcMinMax();
};

#endif
