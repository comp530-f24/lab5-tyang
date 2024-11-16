import os
import time
import random
import argparse

# Function to perform sequential or random I/O operations with the specified size and stride
def perform_io_test(file_path, io_size, stride=0, is_random=False, is_write=True, total_size=1*1024*1024*1024):
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
    flags = os.O_DIRECT | os.O_RDWR | os.O_CREAT
    # flags = os.O_RDWR
    buffer = bytearray(io_size)
    
    try:
        fd = os.open(file_path, flags)
        with os.fdopen(fd, 'r+b') as f:
            start_time = time.monotonic()
            
            offset = 0
            while offset < total_size:
                if is_random:
                    # Randomly choose an offset within range
                    offset = random.randint(0, (total_size - io_size) // io_size) * io_size
                
                # Move to the offset
                f.seek(offset)
                
                # Write or read based on is_write flag
                if is_write:
                    f.write(buffer)
                else:
                    f.read(io_size)
                
                # If not random, add stride to offset for sequential access
                if not is_random:
                    offset += io_size + stride
            
                # Force sync for write operations
                if is_write:
                    f.flush()
                    os.fsync(f.fileno())
            
            # Calculate elapsed time and throughput
            elapsed_time = time.monotonic() - start_time
            throughput = total_size / elapsed_time  # Bytes per second
            
            print(f"{'Write' if is_write else 'Read'} Test")
            print(f"IO Size: {io_size / 1024} KB, Stride: {stride / 1024} KB, Mode: {'Random' if is_random else 'Sequential'}")
            print(f"Throughput: {throughput / (1024 * 1024):.2f} MB/s")
            print(f"Time Taken: {elapsed_time:.2f} seconds")
    
    except PermissionError:
        print("Error: Permission denied. Run as root if accessing a raw device.")
    except Exception as e:
        print(f"Error: {e}")

# Parse command-line arguments for flexibility
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Microbenchmark for I/O performance")
    parser.add_argument("file_path", type=str, help="Path to the file or device to benchmark.")
    parser.add_argument("io_size", type=int, help="Size of each I/O operation in KB.")
    parser.add_argument("--stride", type=int, default=0, help="Stride between sequential I/Os in KB.")
    parser.add_argument("--random", action="store_true", help="Enable random I/O pattern.")
    parser.add_argument("--write", action="store_true", help="Enable write operations (default is read).")
    args = parser.parse_args()
    
    # Run the benchmark
    perform_io_test(
        file_path=args.file_path,
        io_size=args.io_size * 1024,
        stride=args.stride * 1024,
        is_random=args.random,
        is_write=args.write
    )