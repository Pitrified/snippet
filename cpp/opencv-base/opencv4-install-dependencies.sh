# https://www.learnopencv.com/install-opencv-4-on-ubuntu-18-04/
# https://www.pyimagesearch.com/2018/08/15/how-to-install-opencv-4-on-ubuntu/

# boatload of dependencies
sudo apt -y install build-essential
sudo apt -y install checkinstall
sudo apt -y install cmake
sudo apt -y install pkg-config
sudo apt -y install yasm
sudo apt -y install git
sudo apt -y install gfortran
sudo apt -y install libjpeg8-dev
sudo apt -y install libpng-dev
sudo apt -y install software-properties-common

# not needed
# sudo add-apt-repository "deb http://security.ubuntu.com/ubuntu xenial-security main"
# sudo apt -y update
 
sudo apt -y install libjasper1
sudo apt -y install libtiff-dev
sudo apt -y install libavcodec-dev
sudo apt -y install libavformat-dev
sudo apt -y install libswscale-dev
sudo apt -y install libdc1394-22-dev
sudo apt -y install libxine2-dev

sudo apt -y install libv4l-dev
# this is clearer for me
sudo ln -s /usr/include/libv4l1-videodev.h /usr/include/linux/videodev.h
# cd /usr/include/linux
# sudo ln -s -f ../libv4l1-videodev.h videodev.h
# cd "$cwd"
 
sudo apt -y install libgstreamer1.0-dev
sudo apt -y install libgstreamer-plugins-base1.0-dev
sudo apt -y install libgtk2.0-dev
sudo apt -y install libtbb-dev
sudo apt -y install qt5-default
sudo apt -y install libatlas-base-dev
sudo apt -y install libfaac-dev
sudo apt -y install libmp3lame-dev
sudo apt -y install libtheora-dev
sudo apt -y install libvorbis-dev
sudo apt -y install libxvidcore-dev
sudo apt -y install libopencore-amrnb-dev
sudo apt -y install libopencore-amrwb-dev
sudo apt -y install libavresample-dev
sudo apt -y install x264
sudo apt -y install v4l-utils
sudo apt -y install unzip
sudo apt -y install libjpeg-dev
sudo apt -y install libx264-dev
sudo apt -y install libgtk-3-dev

# python dep
# sudo apt -y install python3-dev
# sudo apt -y install python3-pip
# sudo -H pip3 install -U pip numpy



