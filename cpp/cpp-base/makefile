# https://www.cs.swarthmore.edu/~newhall/unixhelp/howto_makefiles.html

# g++ img-display.cpp -o img-display `pkg-config --cflags --libs opencv`
CC = g++

# compiler flags:
# -g    adds debugging information to the executable file
# -Wall turns on most, but not all, compiler warnings
CFLAGS = -Wall -g

OPENCVLIBS = `pkg-config --cflags --libs opencv`

SNIP_CPP=$(wildcard *.cpp)
SNIP_OUT=$(patsubst %.cpp, %.out, $(SNIP_CPP))

# MAIN = pointer-reference

.PHONY : all
all : $(SNIP_OUT)
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
	@echo SNIP_CPP: $(SNIP_CPP)
	@echo SNIP_OUT: $(SNIP_OUT)

.PHONY : help
help : makefile
	@sed -n 's/^##//p' $<
