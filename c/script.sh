#!/bin/bash
# Read each line from experiments.txt and pipe it to ./io_benchmark
while IFS= read -r line; do
    set -- $line
    ./io_benchmark $1 $2 $3 $4 $5 $6 $7
done < experiments_c.txt