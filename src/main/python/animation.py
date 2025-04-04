import os
import re
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.ticker as tick
from tqdm import tqdm


DPI = 100
FIGSIZE=(1920 / DPI, 1080 / DPI)

def y_fmt(x, pos):
    """Format number as power of 10"""
    if x == 0:
        return "0"

    # Get the base and exponent
    base, exp = f"{x:.2e}".split("e")
    base = float(base)
    exp = int(exp)

    # Check if the decimal part is zero (e.g. 1.00 → 1)
    if round(base % 1, 2) == 0:
        base_str = f"{int(base)}"
    else:
        base_str = f"{base:.2f}"
    
    return f"{base_str}x10^{exp}"


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


def extract_seed(filename: str) -> int:
    """Extracts seed from the filename."""
    match = re.search(r"seed-(\d+)", filename)
    if match:
        return int(match.group(1))
    raise ValueError(f"Could not determine seed from filename: {filename}")


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
    fig, ax = plt.subplots(figsize=FIGSIZE)
    img = ax.imshow(grids[0], cmap='gray', vmin=-1, vmax=1)

    ax.yaxis.set_major_formatter(tick.FuncFormatter(y_fmt))
    ax.xaxis.set_major_formatter(tick.FuncFormatter(y_fmt))

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


def plot_magnetization(steps: list[int], magnetization: list[float], output_filename: str,
                       p_value: float, grid_size: int, seed: int):
    """Plots magnetization over time with proper formatting."""
    plt.figure(figsize=FIGSIZE)
    plt.plot(steps, magnetization, marker="o", linestyle="-", markersize=1)
    plt.xlabel("Paso de simulación", fontsize=20)
    plt.ylabel("Magnetización (adimensional)", fontsize=20)
    plt.tick_params(axis='both', labelsize=16)

    # Add configuration information to the side
    ax = plt.gca()
    text = f"Parámetros:\n- Semilla: {seed}\n- Tamaño de grilla: {grid_size}x{grid_size}\n- Probabilidad p: {p_value}"
    plt.text(1.02, 0.5, text, transform=ax.transAxes, fontsize=14, va='center')
 
    ax.yaxis.set_major_formatter(tick.FuncFormatter(y_fmt))
    ax.xaxis.set_major_formatter(tick.FuncFormatter(y_fmt))

    plt.tight_layout()
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


def plot_observable_vs_p(p_values, values, ylabel, filename, config_text):
    """General function to plot observables vs p with proper formatting."""
    plt.figure(figsize=FIGSIZE)
    plt.plot(p_values, values, marker="o", linestyle="-")
    plt.xlabel("Probabilidad p", fontsize=20)
    plt.ylabel(ylabel, fontsize=20)
    plt.tick_params(axis='both', labelsize=16)

    # Add configuration information to the side
    ax = plt.gca()
    plt.text(1.02, 0.5, config_text, transform=ax.transAxes, fontsize=14, va='center')

    ax.yaxis.set_major_formatter(tick.FuncFormatter(y_fmt))
    ax.xaxis.set_major_formatter(tick.FuncFormatter(y_fmt))

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


def main():
    input_dir = "./output"
    output_base_dir = "./analysis"
    os.makedirs(output_base_dir, exist_ok=True)

    results_by_seed: dict[int, list[tuple[float, float, float]]] = {}

    for filename in os.listdir(input_dir):
        if filename.endswith(".csv"):
            filepath = os.path.join(input_dir, filename)
            grid_size = extract_grid_size(filename)
            p_value = extract_p_value(filename)
            seed = extract_seed(filename)

            output_dir = os.path.join(output_base_dir, f"seed-{seed}")
            os.makedirs(output_dir, exist_ok=True)

            grids, magnetization, steps = load_simulation_data(filepath, grid_size)

            # Save magnetization plot
            plot_filename = os.path.join(output_dir, filename.replace(".csv", "_magnetization.png"))
            plot_magnetization(steps, magnetization, plot_filename, p_value, grid_size, seed)
            print(f"[seed {seed}] Magnetization plot saved to {plot_filename}")

            if detect_steady_state(magnetization):
                print(f"[seed {seed}] {filename}: System reached steady state ✅")
            else:
                print(f"[seed {seed}] {filename}: System NOT in steady state ❌")

            avg_M, chi = compute_observables(magnetization)
            results_by_seed.setdefault(seed, []).append((p_value, avg_M, chi))

    # Plot observables per seed
    for seed, results in results_by_seed.items():
        results.sort()
        p_values, avg_M_values, chi_values = zip(*results)
        output_dir = os.path.join(output_base_dir, f"seed-{seed}")

        config_text = f"Parámetros:\n- Semilla: {seed}\n- Tamaño de grilla: {grid_size}x{grid_size}"

        plot_observable_vs_p(
            p_values, avg_M_values,
            "Magnetización promedio (adimensional)",
            os.path.join(output_dir, "magnetization_vs_p.png"),
            config_text
        )

        plot_observable_vs_p(
            p_values, chi_values,
            "Susceptibilidad (adimensional)",
            os.path.join(output_dir, "susceptibility_vs_p.png"),
            config_text
        )

    # Compute average over seeds
    seed_count = len(results_by_seed)
    combined_results: dict[float, list[tuple[float, float]]] = {}
    for seed_results in results_by_seed.values():
        for p, m, chi in seed_results:
            combined_results.setdefault(p, []).append((m, chi))

    avg_output_dir = os.path.join(output_base_dir, "average")
    os.makedirs(avg_output_dir, exist_ok=True)

    avg_results = []
    for p in sorted(combined_results.keys()):
        m_vals = [x[0] for x in combined_results[p]]
        chi_vals = [x[1] for x in combined_results[p]]
        avg_results.append((p, np.mean(m_vals), np.mean(chi_vals)))

    p_values, avg_M_values, chi_values = zip(*avg_results)

    config_text = f"Parámetros:\n- Tamaño de grilla: {grid_size}x{grid_size}\n- Número de semillas: {seed_count}"

    plot_observable_vs_p(
        p_values, avg_M_values,
        "Magnetización promedio (adimensional)",
        os.path.join(avg_output_dir, "avg_magnetization_vs_p.png"),
        config_text
    )

    plot_observable_vs_p(
        p_values, chi_values,
        "Susceptibilidad (adimensional)",
        os.path.join(avg_output_dir, "avg_susceptibility_vs_p.png"),
        config_text
    )


if __name__ == "__main__":
    main()

