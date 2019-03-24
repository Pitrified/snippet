# #### MAKE INFO ####
# $@ means 'the target of the current rule' "results.txt"
# $^ means 'all the dependencies of the current rule'
# 	they need to be explicit (make looks for dats)
# $< means 'the first dependency of the current rule'
# % is a make wildcard
# $* is a special variable which gets replaced by the stem with which the rule matched
# $(...) is a variable reference
# use include to load files

# #### G++ INFO ####
# compile the source code .cpp into .o file:
# 	g++ -c main.cpp
# make is smart and knows that .o are generated from .cpp
# link object files into executable
#   g++ -o main main.o *.o

# www.cs.bu.edu/teaching/cpp/writing-makefiles/
# www.cs.swarthmore.edu/~newhall/unixhelp/howto_makefiles.html

# compiler
CC = g++
# compiler flags:
# -g    adds debugging information to the executable file
# -Wall turns on most, but not all, compiler warnings
CFLAGS = -Wall -g
# additional flags
OPENCVLIBS = `pkg-config --cflags --libs opencv`

# TARGET = main
EXEC_NAME = runme.out

CPP_FILES=$(wildcard *.cpp)
OBJ_FILES=$(patsubst %.cpp, %.o, $(CPP_FILES))

.PHONY : all
all : $(EXEC_NAME)

# pure questo potrebbe essere specifico del progetto
$(EXEC_NAME) : $(OBJ_FILES)
	$(CC) $(CFLAGS) -o $@ $^

# specifichi a mano tutti gli .o
# sono specifici del tuo progetto
main.o : main.cpp Point.h Rectangle.h
	$(CC) $(CFLAGS) -c $<

# magic make: the .cpp dependency is automatic
Point.o : Point.h

Rectangle.o : Rectangle.h Point.h

## clean : remove auto-generated files
.PHONY : clean
clean : 
	rm -f $(EXEC_NAME)
	rm -f $(OBJ_FILES)

## variables : print variables used
.PHONY : variables
variables :
	@echo CPP_FILES : $(CPP_FILES)
	@echo SRC_FILES : $(SRC_FILES)
	@echo HEAD_FILES: $(HEAD_FILES)
	@echo OBJ_FILES : $(OBJ_FILES)

.PHONY : help
help : makefile
	@sed -n 's/^##//p' $<
