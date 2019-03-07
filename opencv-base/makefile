# https://www.cs.swarthmore.edu/~newhall/unixhelp/howto_makefiles.html

# g++ img-display.cpp -o img-display `pkg-config --cflags --libs opencv`
CC = g++

# compiler flags:
# -g    adds debugging information to the executable file
# -Wall turns on most, but not all, compiler warnings
CFLAGS = -Wall -g

OPENCVLIBS = `pkg-config --cflags --libs opencv`

MAIN = img-display

.PHONY : all
all : $(MAIN)
	@echo Compiled successfully opencv project

$(MAIN) : $(MAIN).cpp
	$(CC) $< -o $(MAIN) $(OPENCVLIBS)


## clean : remove auto-generated files
.PHONY : clean
clean : 
	rm -f $(MAIN)

## variables : print variables used
.PHONY : variables
variables :
	@echo MAIN: $(MAIN)

.PHONY : help
help : makefile
	@sed -n 's/^##//p' $<
