# COMPILER = /usr/local/cuda/bin/nvcc
COMPILER = /usr/bin/g++

#FLAGS = -g -G -Xcompiler -Wall -std=c++11
#FLAGS =  -std=c++11 --optimize 3
#FLAGS =  -std=c++11 
#FLAGS = -g -std=c++11 # for gcc
FLAGS = -g


INCLUDE = -I/usr/include/python2.7
# INCLUDE = -I/usr/include/python3.4


all: main.exe

main.exe: main.o 
	$(COMPILER) $^ -o $@ -lpython2.7

main.o: main.cpp 
	$(COMPILER) $(FLAGS) $(INCLUDE) -c $< -o $@ 

cleanAll:

plots: all
