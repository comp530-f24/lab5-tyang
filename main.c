/* -*- mode:c; c-file-style:"k&r"; c-basic-offset: 4; tab-width:4;
 * indent-tabs-mode:nil; mode:auto-fill; fill-column:78; -*- */
/* vim: set ts=4 sw=4 et tw=78 fo=cqt wm=0: */

/* Multi-threaded LRU Simulation.
 *
 * Don Porter - porter@cs.unc.edu
 *
 * COMP 530 - University of North Carolina, Chapel Hill
 *
 */

#include <assert.h>
#include <ctype.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <unistd.h>

void help() {
  printf("LRU Simulator.  Usage: ./lru-[variant] [options]\n\n");
  printf("Options:\n");
  printf("\t-c numclients - Use numclients threads.\n");
  printf("\t-h - Print this help.\n");
  printf("\t-l length - Run clients for length seconds.\n");
  printf("\n\n");
}

int main(int argc, char **argv) {
  int numthreads = 1; // default to 1
  int c;

  // Read options from command line:
  //   # clients from command line, as well as seed file
  //   Simulation length
  while ((c = getopt(argc, argv, "c:hl:s:")) != -1) {
    switch (c) {
    case 'c':
      numthreads = atoi(optarg);
      printf("numthreads, %d", numthreads);
    case 'h':
      help();
      return 0;
    case 'l':
      break;
    case 's':
      break;
    default:
      printf("Unknown option\n");
      help();
      return 1;
    }
  }
}

int open_disk(char *filename) {
    int fd = open(filename, O_RDWR);
    #include <fcntl.h>

    int fd = open(filename, O_RDWR | O_DIRECT);
    if (fd < 0) {
        perror("open");
        exit(1);
    }
    return fd;  
}
