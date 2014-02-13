all : record recordpp

record : record.c
	gcc -o record record.c `pkg-config --cflags --libs opencv`

recordpp : record.cpp
	g++ -o recordpp record.cpp `pkg-config --cflags --libs opencv`

