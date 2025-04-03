grid_size=50
steps=20000
seed=1743645648280
output_directory=./output
probabilities=(0.05 0.08 0.10 0.12 0.14 0.16 0.18 0.20 0.22 0.25)

clear
gradle clean build

for p in "${probabilities[@]}"; do
  echo "Running simulation with p=$p"
  gradle run --no-build-cache --rerun-tasks --args="\
    --grid-size=${grid_size} \
    --probability=${p} \
    --steps=${steps} \
    --seed=${seed} \
    --output-directory=${output_directory}"
done

