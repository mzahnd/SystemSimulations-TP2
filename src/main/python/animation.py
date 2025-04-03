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


def extract_p_value(filename: str) -> float:
    """Extracts probability p from the filename."""
    match = re.search(r"p-([0-9\.]+)", filename)
    if match:
        return float(match.group(1))
    raise ValueError(f"Could not determine p value from filename: {filename}")


def load_simulation_data(filepath: str, grid_size: int) -> tuple[list[np.ndarray], list[float], list[int]]:
    """Loads simulation data from a CSV file dynamically based on grid size."""
    df = pd.read_csv(filepath, header=None)
    steps = df.iloc[:, 0].tolist()
    magnetization = df.iloc[:, 1].tolist()
    start_index = 2  # First two columns are step and magnetization
    end_index = start_index + grid_size ** 2
    grids = [row[start_index:end_index].values.reshape((grid_size, grid_size)) for _, row in df.iterrows()]
    return grids, magnetization, steps


def animate_simulation(grids: list[np.ndarray], output_filename: str):
    """Generates an animation of the grid evolution with a progress bar."""
    fig, ax = plt.subplots()
    img = ax.imshow(grids[0], cmap='gray', vmin=-1, vmax=1)

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


def plot_magnetization(steps: list[int], magnetization: list[float], output_filename: str):
    """Plots magnetization over time to visualize steady-state behavior."""
    plt.figure(figsize=(8, 5))
    plt.plot(steps, magnetization, marker="o", linestyle="-", markersize=3)
    plt.xlabel("Simulation Step")
    plt.ylabel("Magnetization")
    plt.title("Magnetization over time")
    plt.grid()
    plt.savefig(output_filename)
    plt.close()


def compute_observables(magnetization: list[float], steady_state_cutoff: int = 5000) -> tuple[float, float]:
    """Computes the time-averaged magnetization and susceptibility after reaching steady state."""
    steady_state_magnetization = magnetization[-steady_state_cutoff:]
    avg_magnetization = np.mean(steady_state_magnetization)
    susceptibility = np.var(steady_state_magnetization)
    return avg_magnetization, susceptibility


def detect_steady_state(magnetization: list[float], threshold: float = 0.001, window: int = 100) -> bool:
    """Checks if the magnetization has stabilized by looking at recent values."""
    if len(magnetization) < window:
        return False
    recent_values = magnetization[-window:]
    max_var = max(recent_values) - min(recent_values)
    return max_var < threshold


def main():
    input_dir = "./output"
    output_dir = "./analysis"
    os.makedirs(output_dir, exist_ok=True)

    results = []
    for filename in os.listdir(input_dir):
        if filename.endswith(".csv"):
            filepath = os.path.join(input_dir, filename)
            grid_size = extract_grid_size(filename)
            p_value = extract_p_value(filename)
            grids, magnetization, steps = load_simulation_data(filepath, grid_size)

            # Save magnetization plot
            plot_filename = os.path.join(output_dir, filename.replace(".csv", "_magnetization.png"))
            plot_magnetization(steps, magnetization, plot_filename)
            print(f"Magnetization plot saved to {plot_filename}")

            # Check steady state
            if detect_steady_state(magnetization):
                print(f"{filename}: System reached steady state ✅")
            else:
                print(f"{filename}: System NOT in steady state ❌")

            # Compute observables
            avg_M, chi = compute_observables(magnetization)
            results.append((p_value, avg_M, chi))

            # Generate animation
            #animation_filename = os.path.join(output_dir, filename.replace(".csv", ".mp4"))
            #animate_simulation(grids, animation_filename)
            #print(f"Animation saved to {animation_filename}")

    # Sort results by p-value
    results.sort()
    p_values, avg_M_values, chi_values = zip(*results)

    # Plot observables vs p
    plt.figure(figsize=(8, 5))
    plt.plot(p_values, avg_M_values, marker="o", linestyle="-", label="<M>")
    plt.xlabel("p")
    plt.ylabel("<M>")
    plt.legend()
    plt.grid()
    plt.title("Magnetization vs p")
    plt.savefig(os.path.join(output_dir, "magnetization_vs_p.png"))
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(p_values, chi_values, marker="o", linestyle="-", color="r", label="χ")
    plt.xlabel("p")
    plt.ylabel("χ")
    plt.legend()
    plt.grid()
    plt.title("Susceptibility vs p")
    plt.savefig(os.path.join(output_dir, "susceptibility_vs_p.png"))
    plt.close()

    print("Analysis complete. Observables saved.")


if __name__ == "__main__":
    main()


