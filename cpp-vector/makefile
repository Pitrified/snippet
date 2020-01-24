# https://www.cs.swarthmore.edu/~newhall/unixhelp/howto_makefiles.html

# g++ img-display.cpp -o img-display `pkg-config --cflags --libs opencv`
CC = g++

# compiler flags:
# -g    adds debugging information to the executable file
# -Wall turns on most, but not all, compiler warnings
CFLAGS = -Wall -g

OPENCVLIBS = `pkg-config --cflags --libs opencv`

# SNIP_CPP=$(wildcard *.cpp)
# SNIP_OUT=$(patsubst %.cpp, %.out, $(SNIP_CPP))

MAIN = str_vec

.PHONY : all
all : $(MAIN).out
	@echo Compiled successfully all snippets

%.out : %.cpp
	$(CC) $< -o $@ $(OPENCVLIBS)

## clean : remove auto-generated files
.PHONY : clean
clean : 
	rm -f *.out

## variables : print variables used
.PHONY : variables
variables :
	@echo MAIN: $(MAIN)

.PHONY : help
help : makefile
	@sed -n 's/^##//p' $<
