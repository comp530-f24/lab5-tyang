import os
import time
import random
import argparse
from sys import platform
import mmap

# Function to perform sequential or random I/O operations with the specified size and stride
def perform_io_test(file_path, io_size, stride=0, is_random=False, is_write=True, total_size=1*1024*1024*1024, desired_iops = 1024 * 1024 * 1024):
    """Perform I/O operations on a specified file or device.
    
    Args:
        file_path (str): Path to file or device to benchmark.
        io_size (int): Size of each I/O operation in bytes.
        stride (int): Stride to apply between each sequential I/O, in bytes.
        is_random (bool): If True, use random offsets; otherwise, use sequential.
        is_write (bool): If True, perform write operations; otherwise, perform reads.
        total_size (int): Total data to write in bytes.
    """
    # Open file with O_DIRECT for direct I/O to avoid OS-level caching
    if platform == "linux" or platform == "linux2":
        flags = os.O_DIRECT | os.O_RDWR | os.O_CREAT
    else: 
        flags = os.O_RDWR | os.O_CREAT
        
    total_iops = 0
    
    fd = os.open(file_path, flags)

    start_time = time.monotonic()
        
    offset = -io_size
    while total_iops < desired_iops:
        if is_random:
            # Randomly choose an offset within range
            offset = random.randint(0, (total_size - io_size) // io_size) * io_size
        if not is_random:
            offset += io_size + stride

        # The SSD is 512mb in size, we must stay below this limit
        if offset + io_size > 1024 * 1024 * 512:
            offset = offset % (1024 * 1024 * 512)

        #make offset a multiple of 512
        offset = offset - offset % 4096

        # Move to the offset
        print(offset)
        os.lseek(fd, offset, os.SEEK_SET)
        
        # Write or read based on is_write flag
        if is_write:
            m = mmap.mmap(-1, io_size)
            os.write(fd, m)
        else:
            # make read_size a multiple of 512
            m = mmap.mmap(-1, io_size)
            f = os.fdopen(fd, 'rb', closefd=False)
            f.readinto(m)
        
        # Force sync for write operations
        if is_write:
            os.fsync(fd)

        total_iops += io_size
    
    # Calculate elapsed time and throughput
    elapsed_time = time.monotonic() - start_time
    throughput = desired_iops / elapsed_time  # Bytes per second
    
    print(f"{'Write' if is_write else 'Read'} Test")
    print(f"IO Size: {io_size / 1024} KB, Stride: {stride / 1024} KB, Mode: {'Random' if is_random else 'Sequential'}")
    print(f"Throughput: {throughput / (1024 * 1024):.2f} MB/s")
    print(f"Time Taken: {elapsed_time:.2f} seconds")

    if file_path.startswith("/dev/"):
        os.close(fd)
    else:
        os.remove(file_path)
    return throughput

def run_experiments(cli_args):
    with open(cli_args.experiment_file, "r") as f:
        with open("results.txt", "w") as out:
            for line in f:
                if line.startswith("#"):
                    continue
                args = line.split()
                throughput = perform_io_test(
                    file_path=cli_args.file_path,
                    io_size=int(args[0]) * 1024,
                    stride=int(args[1]) * 1024,
                    is_random=args[2] == "random",
                    is_write=args[3] == "write",
                    total_size=int(args[4]) * 1024,
                    desired_iops=int(args[5]) * 1024
                )
                print(f"Throughput: {throughput / (1024 * 1024):.2f} MB/s for {line}")
                out.write(f"{throughput / (1024 * 1024):.2f}\n")

# Parse command-line arguments for flexibility
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Microbenchmark for I/O performance")
    parser.add_argument("--file-path", type=str, help="Path to the file or device to benchmark.")
    parser.add_argument("--io-size", type=int, help="Size of each I/O operation in KB.")
    parser.add_argument("--stride", type=int, default=0, help="Stride between sequential I/Os in KB.")
    parser.add_argument("--random", action="store_true", help="Enable random I/O pattern.")
    parser.add_argument("--write", action="store_true", help="Enable write operations (default is read).")
    parser.add_argument("--run-experiment", action="store_true", help="Run from experiment file.")
    parser.add_argument("--experiment-file", type=str, help="Specify experiment file.")
    args = parser.parse_args()
    
    if args.run_experiment:
        run_experiments(args)
        exit(0)

    # Run the benchmark
    perform_io_test(
        file_path=args.file_path,
        io_size=args.io_size * 1024,
        stride=args.stride * 1024,
        is_random=args.random,
        is_write=args.write
    )
