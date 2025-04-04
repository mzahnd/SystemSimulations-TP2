#!/bin/bash

# Simulation parameters
grid_size=50
steps=50000  # The simulation must run long enough to reach a steady state
output_directory=./output
probabilities=(0.01 0.1 0.9)
seed=1743645648280

# Clear the terminal
clear

# Build the project
gradle clean build

# Run the simulations with different seeds
echo "Running animation simulation with seed $seed and probabilities: ${probabilities[*]}"

gradle run --no-build-cache --rerun-tasks --args="\
  --grid-size=${grid_size} \
  --steps=${steps} \
  --seed=${seed} \
  --output-directory=${output_directory} $(printf ' --probability=%s' "${probabilities[@]}")"

