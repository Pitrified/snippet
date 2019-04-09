cmake_minimum_required(VERSION 3.2)

project(Waver)

add_definitions("-std=c++11")

find_package(OpenCV REQUIRED)
include_directories(
	include
	${OpenCV_INCLUDE_DIRS}
)

add_library(Waver
  src/main.cpp
  include/waver.h
)
target_link_libraries(Waver
  ${OpenCV_LIBRARIES}
)
add_executable(main
  src/main.cpp
  src/waver.cpp
)

target_link_libraries(main
    Waver
)
