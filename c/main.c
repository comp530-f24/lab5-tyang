#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/time.h>
#include <string.h>
#include <errno.h>
#include <stdbool.h>

#define BUFFER_SIZE (1024 * 1024) // 1 MB buffer size

// Function to get current time in seconds
double get_time() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec + (tv.tv_usec / 1000000.0);
}

// Perform I/O operations
void perform_io_test(const char *file_path, size_t io_size, size_t stride, bool is_random, bool is_write, 
                     size_t total_size, size_t desired_iops) {
    int flags = O_RDWR | O_CREAT;
#ifdef __linux__
    flags |= O_DIRECT; // Enable direct I/O on Linux
#endif

    int fd = open(file_path, flags, 0666);
    if (fd < 0) {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }

    void *buffer = aligned_alloc(4096, BUFFER_SIZE);
    if (!buffer) {
        perror("Error allocating buffer");
        close(fd);
        exit(EXIT_FAILURE);
    }
    memset(buffer, 0, BUFFER_SIZE); // Initialize buffer to zero

    size_t total_iops = 0;
    size_t offset = 0;

    double start_time = get_time();

    while (total_iops < desired_iops) {
        if (is_random) {
            // Generate a random offset within the valid range
            offset = (rand() % ((total_size - io_size) / io_size)) * io_size;
        } else {
            offset += io_size + stride;

            // Ensure the offset stays within bounds
            if (offset + io_size > total_size) {
                offset = offset % total_size;
            }
        }

        // Perform the write or read operation
        if (lseek(fd, offset, SEEK_SET) < 0) {
            perror("Error seeking");
            free(buffer);
            close(fd);
            exit(EXIT_FAILURE);
        }

        if (is_write) {
            if (write(fd, buffer, io_size) != io_size) {
                perror("Error writing");
                free(buffer);
                close(fd);
                exit(EXIT_FAILURE);
            }
        } else {
            if (read(fd, buffer, io_size) != io_size) {
                perror("Error reading");
                free(buffer);
                close(fd);
                exit(EXIT_FAILURE);
            }
        }

        // Sync for write operations
        if (is_write) {
            fsync(fd);
        }

        total_iops += io_size;
    }

    double elapsed_time = get_time() - start_time;
    double throughput = (double)(desired_iops) / elapsed_time; // Bytes per second

    printf("%s Test\n", is_write ? "Write" : "Read");
    printf("IO Size: %.2f KB, Stride: %.2f KB, Mode: %s\n", io_size / 1024.0, stride / 1024.0, is_random ? "Random" : "Sequential");
    printf("Throughput: %.2f MB/s\n", throughput / (1024 * 1024));
    printf("Time Taken: %.2f seconds\n", elapsed_time);

    free(buffer);
    close(fd);

    // If the file is not a device, remove it
    if (strncmp(file_path, "/dev/", 5) != 0) {
        unlink(file_path);
    }
}

// Main function to parse command-line arguments
int main(int argc, char *argv[]) {
    if (argc < 7) {
        fprintf(stderr, "Usage: %s <file_path> <io_size_kb> <stride_kb> <random> <write> <total_size_mb> <desired_iops_mb>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *file_path = argv[1];
    size_t io_size = atoi(argv[2]) * 1024;       // Convert KB to bytes
    size_t stride = atoi(argv[3]) * 1024;       // Convert KB to bytes
    bool is_random = atoi(argv[4]) != 0;
    bool is_write = atoi(argv[5]) != 0;
    size_t total_size = atoi(argv[6]) * 1024 * 1024;  // Convert MB to bytes
    size_t desired_iops = atoi(argv[7]) * 1024 * 1024; // Convert MB to bytes

    perform_io_test(file_path, io_size, stride, is_random, is_write, total_size, desired_iops);

    return EXIT_SUCCESS;
}