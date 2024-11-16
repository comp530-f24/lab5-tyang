all: main

CFLAGS += -g -Wall -Werror -pthread

%.o: %.c *.h
	gcc $(CFLAGS) -c -o $@ $<

main: main.c
	gcc $(CFLAGS) main.c
