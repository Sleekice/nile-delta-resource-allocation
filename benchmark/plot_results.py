
"""
Nile Delta Resource Allocation - Phase 3 Performance Visualization

Author: Peter Nwochie Tiewah
Institution: University of the Cumberlands
Course: MSCS 532 - Algorithms and Data Structures
Instructor: Dr. Michael Solomon
Project: Phase 3 - Optimization, Scaling, and Final Evaluation
Date: November 2026

Description:
    This module generates performance graphs comparing the original
    ResourceGraph from Phase 2 with the OptimizedResourceGraph from Phase 3.

    It reads the recorded benchmark measurements from a CSV file and
    focuses on node deletion, which is the main operation optimized
    through reverse-adjacency indexing.

    Two visualizations are produced:
    1. A line graph comparing node-deletion execution times.
    2. A bar graph showing the speedup achieved by the optimized graph.

Input:
    results/benchmark_results.csv

Output:
    figures/performance_graph.png

Purpose:
    The resulting figure supports the Phase 3 performance analysis
    by illustrating how node-deletion efficiency changes as the
    network grows from 1,000 to 20,000 vertices.

    The script uses previously recorded benchmark measurements.
    It does not rerun the benchmarks or modify the CSV data.

Usage:
    python3 -m benchmark.plot_results
"""

import csv
from pathlib import Path

import matplotlib.pyplot as plt


# Locate the project root so file paths work regardless of the working directory.
ROOT = Path(__file__).resolve().parent.parent
RESULTS_FILE = ROOT / "results" / "benchmark_results.csv"
FIGURES_FOLDER = ROOT / "figures"

# Create the figures folder if it does not already exist.
FIGURES_FOLDER.mkdir(exist_ok=True)


def load_deletion_results():
    """Read the CSV and extract node-deletion times and speedup ratios."""

    sizes = []
    baseline_times = []
    optimized_times = []
    speedups = []

    with RESULTS_FILE.open(newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            # Ignore the other operations because this figure focuses
            # on the improvement made to node deletion.
            if row["operation"] != "remove_node":
                continue

            # Convert CSV strings into numeric values for plotting.
            sizes.append(int(row["vertices"]))
            baseline_times.append(float(row["baseline"]))
            optimized_times.append(float(row["optimized"]))
            speedups.append(float(row["baseline_over_optimized"]))

    # Avoid creating an empty graph if the expected measurements are missing.
    if not sizes:
        raise ValueError("No node-deletion measurements found.")

    return sizes, baseline_times, optimized_times, speedups


def main():
    """Generate and save the Phase 2 versus Phase 3 performance figure."""

    sizes, baseline, optimized, speedups = load_deletion_results()

    # Place execution times and speedup measurements side by side.
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Compare both implementations using the same graph sizes.
    axes[0].plot(
        sizes, baseline,
        marker="o",
        linewidth=2.5,
        color="#2563EB",
        label="Phase 2: Original"
    )

    axes[0].plot(
        sizes, optimized,
        marker="s",
        linewidth=2.5,
        color="#F97316",
        label="Phase 3: Optimized"
    )

    axes[0].set_title("Node Deletion Performance")
    axes[0].set_xlabel("Number of Vertices")
    axes[0].set_ylabel("Execution Time (ms)")
    axes[0].set_xticks(sizes)
    axes[0].tick_params(axis="x", labelrotation=30)
    axes[0].grid(True, linestyle="--", alpha=0.3)
    axes[0].legend()

    # Display how many times faster the optimized deletion is at each size.
    bars = axes[1].bar(
        [f"{size:,}" for size in sizes],
        speedups,
        color="#16A34A",
        width=0.6
    )

    axes[1].set_title("Phase 3 Node Deletion Speedup")
    axes[1].set_xlabel("Number of Vertices")
    axes[1].set_ylabel("Speedup (times faster)")
    axes[1].set_ylim(0, max(speedups) * 1.2)
    axes[1].grid(axis="y", linestyle="--", alpha=0.3)
    axes[1].set_axisbelow(True)

    # Add the speedup value above each bar for easier comparison.
    for bar, speedup in zip(bars, speedups):
        axes[1].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(speedups) * 0.025,
            f"{speedup:.1f}x",
            ha="center",
            fontsize=10
        )

    fig.suptitle(
        "Nile Delta Resource Graph: Phase 2 vs Phase 3",
        fontsize=14,
        fontweight="bold"
    )

    # Adjust spacing so titles and axis labels do not overlap.
    fig.tight_layout()

    # Save the figure at a resolution suitable for the academic report.
    output = FIGURES_FOLDER / "performance_graph.png"
    fig.savefig(output, dpi=300, bbox_inches="tight")

    # Close the figure to release resources after saving it.
    plt.close(fig)

    print(f"Graph saved to: {output}")


if __name__ == "__main__":
    main()
