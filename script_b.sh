#!/bin/bash

# Simulation parameters
grid_size=50
steps=100000  # Ensuring enough steps to confirm steady state
output_directory=./output
probabilities=(0.01 0.1 0.9)
seeds=(1743645648280 9876543210)

# Clear the terminal
clear

# Build the project
gradle clean build

# Run the simulations with different seeds
for seed in "${seeds[@]}"; do
  echo "Running consensus evolution simulation with seed $seed and probabilities: ${probabilities[*]}"

  gradle run --no-build-cache --rerun-tasks --args="\
    --grid-size=${grid_size} \
    --steps=${steps} \
    --seed=${seed} \
    --output-directory=${output_directory} $(printf ' --probability=%s' "${probabilities[@]}")"
done

