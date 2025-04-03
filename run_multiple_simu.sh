#!/bin/bash

# Simulation parameters
grid_size=50
steps=20000
seed=1743645648280
output_directory=./output
probabilities=(0.05 0.08 0.10 0.12 0.14 0.16 0.18 0.20 0.22 0.25)

# Clear the terminal
clear

# Build the project
gradle clean build

# Construct the probabilities argument by repeating --probability
probability_args=""
for p in "${probabilities[@]}"; do
  probability_args+=" --probability=${p}"
done

# Run the simulation
echo "Running simulation with probabilities: ${probabilities[*]}"

gradle run --no-build-cache --rerun-tasks --args="\
  --grid-size=${grid_size} \
  --steps=${steps} \
  --seed=${seed} \
  --output-directory=${output_directory} ${probability_args}"

