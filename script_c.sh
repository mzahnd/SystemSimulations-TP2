#!/bin/bash

# Simulation parameters
grid_size=50
steps=100000  # The simulation must reach steady state
output_directory=./output
probabilities=(0.02 0.04 0.06 0.08 0.10 0.12 0.14 0.16 0.18 0.20)
seed=1743645648280

# Clear the terminal
clear

# Build the project
gradle clean build

# Run the simulations with different seeds
echo "Running observables simulation with seed $seed and probabilities: ${probabilities[*]}"

gradle run --no-build-cache --rerun-tasks --args="\
  --grid-size=${grid_size} \
  --steps=${steps} \
  --seed=${seed} \
  --output-directory=${output_directory} $(printf ' --probability=%s' "${probabilities[@]}")"

