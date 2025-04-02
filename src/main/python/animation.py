import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from tqdm import tqdm

def extract_grid_size(filename: str) -> int:
    """Extracts grid size from the filename (e.g., 'n-50_s-20000_p-0.1_seed-123.csv')."""
    match = re.search(r"n-(\d+)", filename)
    if match:
        return int(match.group(1))
    raise ValueError(f"Could not determine grid size from filename: {filename}")

def load_simulation_data(filepath: str, grid_size: int) -> tuple[list[np.ndarray], list[float]]:
    """Loads simulation data from a CSV file dynamically based on grid size."""
    df = pd.read_csv(filepath, header=None)
    steps = df.iloc[:, 0].tolist()
    magnetization = df.iloc[:, 1].tolist()
    start_index = 2  # First two columns are step and magnetization
    end_index = start_index + grid_size ** 2
    grids = [row[start_index:end_index].values.reshape((grid_size, grid_size)) for _, row in df.iterrows()]
    return grids, magnetization

def animate_simulation(grids: list[np.ndarray], output_filename: str):
    """Generates an animation of the grid evolution with a progress bar."""
    fig, ax = plt.subplots()
    img = ax.imshow(grids[0], cmap='gray', vmin=0, vmax=1)

    frames = len(grids)
    pbar = tqdm(total=frames, desc="Generating animation")

    def update(frame):
        img.set_array(grids[frame])
        ax.set_title(f"Step {frame}")
        pbar.update(1)
        return img,

    ani = animation.FuncAnimation(fig, update, frames=frames, interval=200)
    ani.save(output_filename, writer=animation.FFMpegWriter(fps=5))
    pbar.close()

def main():
    input_dir = "./output"
    output_dir = "./animations"
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith(".csv"):
            filepath = os.path.join(input_dir, filename)
            grid_size = extract_grid_size(filename)
            grids, _ = load_simulation_data(filepath, grid_size)
            output_filename = os.path.join(output_dir, filename.replace(".csv", ".mp4"))
            animate_simulation(grids, output_filename)
            print(f"Animation saved to {output_filename}")

if __name__ == "__main__":
    main()


