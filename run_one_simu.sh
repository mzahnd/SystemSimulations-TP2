grid_size=50
probability=0.1
steps=50000
seed=1743645648280
output_directory=./output

clear
gradle clean build

gradle run --no-build-cache --rerun-tasks --args="\
  --grid-size=${grid_size} \
  --probability=${probability} \
  --steps=${steps} \
  --seed=${seed} \
  --output-directory=${output_directory}"

