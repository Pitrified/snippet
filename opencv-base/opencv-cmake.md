# Build OpenCV 4 from source, with contrib modules

Useful guides:
* <https://www.pyimagesearch.com/2018/08/15/how-to-install-opencv-4-on-ubuntu/>
* <https://www.learnopencv.com/install-opencv-4-on-ubuntu-18-04/>

This probably tells where to put the library, leave it empty
```
-D OPENCV_PYTHON3_INSTALL_PATH=/usr/local/lib/python3.6/dist-packages \
```

This tells where to install opencv
```
-D CMAKE_INSTALL_PREFIX=~/.local \
```

This tells where the contrib modules are, and enables them
```
-D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
-D OPENCV_ENABLE_NONFREE=ON \
```

Complete cmake options
```
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=~/.local \
    -D INSTALL_C_EXAMPLES=ON \
    -D INSTALL_PYTHON_EXAMPLES=ON \
    -D WITH_TBB=ON \
    -D WITH_V4L=ON \
#   -D OPENCV_PYTHON3_INSTALL_PATH=/usr/local/lib/python3.6/dist-packages \
    -D WITH_QT=ON \
    -D WITH_OPENGL=ON \
    -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
    -D OPENCV_ENABLE_NONFREE=ON \
    -D BUILD_EXAMPLES=ON ..
```

Use `locate cv2 | grep python` to find the library, look for something like
```
~/.local/lib/python3.6/dist-packages/cv2/python-3.6/cv2.cpython-36m-x86_64-linux-gnu.so
```

Create a virtualenv and symlink the library in its `site-packages`
```
~$ cd ~/.virtualenvs/cv4c/lib/python3.6/site-packages/
~/.virtualenvs/cv4c/lib/python3.6/site-packages$ ln -s ~/.local/lib/python3.6/dist-packages/cv2/python-3.6/cv2.cpython-36m-x86_64-linux-gnu.so cv2.so
```

Test the installation, use the contrib module
```
~$ python3
>>> import cv2
>>> cv2.__version__
'4.1.0'
>>> cv2.xfeatures2d.SIFT_create(400)
<xfeatures2d_SIFT 0x7f997d63e730>
```
