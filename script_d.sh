#!/bin/bash

# Simulation parameters
grid_sizes=(30 50 70 100)  # One smaller (30) and two larger (70, 100)
steps=100000  # Ensure reaching steady state
output_directory=./output
probabilities=(0.02 0.04 0.06 0.08 0.10 0.12 0.14 0.16 0.18 0.20)
seed=1743645648280

# Clear the terminal
clear

# Build the project
gradle clean build

# Run the simulations with different grid sizes and seeds
for grid_size in "${grid_sizes[@]}"; do
  echo "Running simulation for grid size $grid_size with seed $seed and probabilities: ${probabilities[*]}"

  gradle run --no-build-cache --rerun-tasks --args="\
    --grid-size=${grid_size} \
    --steps=${steps} \
    --seed=${seed} \
    --output-directory=${output_directory} $(printf ' --probability=%s' "${probabilities[@]}")"
done

