cmake_minimum_required(VERSION 3.2)

project(Lab3)

add_definitions("-std=c++11")

find_package(OpenCV REQUIRED)
include_directories(
	include
	${OpenCV_INCLUDE_DIRS}
)

add_library(Lab3
  src/main.cpp
  include/show_histogram_function.h
  include/equalizer.h
  include/filter.h
  include/gaussianFilter.h
  include/medianFilter.h
  include/BilateralFilter.h
)
target_link_libraries(Lab3
  ${OpenCV_LIBRARIES}
)
add_executable(main
  src/main.cpp
  src/show_histogram_function.cpp
  src/equalizer.cpp
  src/filter.cpp
  src/gaussianFilter.cpp
  src/medianFilter.cpp
  src/BilateralFilter.cpp
)

target_link_libraries(main
    Lab3
)




