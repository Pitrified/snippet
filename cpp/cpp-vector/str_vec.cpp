#include <iostream>
#include <vector>
// #include <opencv2/opencv.hpp>

// using namespace cv;
using namespace std;

int main(int argc, char** argv)
{
    int img_max = 3;
    vector<string> nomi_img(img_max);
    for (int i=1; i<=img_max; i++) {
        // if (i<10) {
            nomi_img[i] = "./immagini/000" + to_string(i) + ".jpg";
        // }
        // else {
            // nomi_img[i] = "./immagini/00" + to_string(i) + ".jpg";
        // }
    }
    return 0;
}

