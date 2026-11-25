
"""
Nile Delta Resource Allocation - Phase 3 Performance Benchmark

Author: Peter Nwochie Tiewah
Institution: University of the Cumberlands
Course: MSCS 532 - Algorithms and Data Structures
Instructor: Dr. Michael Solomon
Project: Phase 3 - Optimization, Scaling, and Final Evaluation
Date: November 2026

Description:
    This module evaluates the performance and scalability of the Nile Delta
    water-distribution graph developed throughout the course project.

    The original ResourceGraph implementation from Phase 2 serves as the
    baseline. It is compared against the OptimizedResourceGraph introduced
    in Phase 3, which uses a reverse-adjacency index to improve node deletion.

    Both implementations are tested using identical synthetic directed
    graphs containing 1,000, 5,000, 10,000, and 20,000 vertices. Each vertex
    connects to up to three subsequent vertices to create a sparse network.

Operations Evaluated:
    - Graph construction time
    - Node lookup performance
    - Breadth-first search (BFS)
    - Depth-first search (DFS)
    - Node deletion performance
    - Peak traced Python memory usage

Benchmark Methodology:
    Execution time is measured using time.perf_counter_ns().
    Each operation is measured nine times, except graph construction,
    which uses five trials. The median is reported to reduce the
    influence of unusually high or low timing measurements.

    Garbage collection is temporarily disabled during timing operations
    to reduce interference. Memory usage is measured separately using
    tracemalloc, which tracks Python allocations rather than total
    operating-system memory consumption.

Output Files:
    results/benchmark_results.csv
        Stores the recorded measurements for each graph size and operation.

    results/environment.txt
        Records the Python version, operating system, graph sizes,
        and benchmark configuration for reproducibility.

Purpose:
    The results support the Phase 3 evaluation of time complexity,
    scalability, memory overhead, and the trade-offs introduced by
    reverse-adjacency indexing.

    This benchmark uses synthetic graph data and does not simulate
    actual water movement or hydraulic behavior.

Usage:
    Run from the project root using:

    python3 -m benchmark.benchmark_phase3
"""


"""Compare the performance of the original and optimized Nile Delta graphs."""

import csv
import gc
import platform
import statistics
import sys
import time
import tracemalloc
from pathlib import Path

from src.resource_graph import ResourceGraph
from src.optimized_graph import OptimizedResourceGraph


# Store benchmark results in the project's results folder.
RESULTS = Path("results")

# Test progressively larger graphs to see how performance changes.
SIZES = (1000, 5000, 10000, 20000)

# Repeat measurements to reduce the effect of timing fluctuations.
TRIALS = 9


def make_graph(cls, size):
    """Create a directed graph with a predictable number of connections."""

    # Use the supplied graph class so both implementations get identical data.
    graph = cls()

    # Create the vertices before connecting them with edges.
    for i in range(size):
        graph.add_node(str(i), f"Node {i}", "canal")

    # Connect each vertex to up to three following vertices.
    # This keeps the graph sparse as the number of vertices increases.
    for i in range(size):
        for delta in (1, 2, 3):
            if i + delta < size:
                graph.add_edge(str(i), str(i + delta), 100)

    return graph


def measure_call(fn, trials=TRIALS):
    """Run an operation several times and return its median time in milliseconds."""

    samples = []

    for _ in range(trials):
        # Pause garbage collection so it is less likely to affect timing.
        gc.disable()

        try:
            # perf_counter_ns provides a high-resolution timing measurement.
            start = time.perf_counter_ns()

            fn()

            # Convert the elapsed time from nanoseconds to milliseconds.
            elapsed = (time.perf_counter_ns() - start) / 1_000_000
            samples.append(elapsed)

        finally:
            # Always restore garbage collection after each measurement.
            gc.enable()

    # The median is less affected by unusually slow or fast measurements.
    return statistics.median(samples)


def measure_build(cls, size):
    """Measure how long it takes to construct a complete graph."""

    # A new graph is created each time instead of reusing an existing graph.
    # Construction is measured five times to limit benchmark overhead.
    return measure_call(lambda: make_graph(cls, size), trials=5)


def measure_delete(cls, size):
    """Measure the time required to delete a vertex from the graph."""

    samples = []

    for _ in range(TRIALS):
        # Build a fresh graph because deleting a node changes its structure.
        graph = make_graph(cls, size)

        # Delete a vertex near the middle of the graph.
        # Its number of connections stays small as graph size increases.
        node = str(size // 2)

        gc.disable()

        try:
            start = time.perf_counter_ns()

            graph.remove_node(node)

            elapsed = (time.perf_counter_ns() - start) / 1_000_000
            samples.append(elapsed)

        finally:
            gc.enable()

        # Confirm the vertex was actually removed.
        assert graph.find_node(node) is None

        # The optimized graph also needs to maintain its reverse-edge index.
        if isinstance(graph, OptimizedResourceGraph):
            assert graph.check_index()

    return statistics.median(samples)


def peak_memory(cls, size):
    """Measure peak traced Python memory while constructing a graph."""

    # Start tracking Python allocations before building the graph.
    tracemalloc.start()

    graph = make_graph(cls, size)

    # We only need the peak memory recorded during construction.
    _, peak = tracemalloc.get_traced_memory()

    tracemalloc.stop()

    # Release the graph after recording its memory usage.
    del graph

    # Convert bytes to mebibytes (MiB).
    return peak / 1024 / 1024


def run():
    """Compare both graph implementations and save their measurements."""

    # Create the results folder if it does not already exist.
    RESULTS.mkdir(exist_ok=True)

    rows = []

    for size in SIZES:
        print(f"Benchmarking {size:,} vertices...", flush=True)

        # Build equivalent graphs for operations that do not modify them.
        baseline = make_graph(ResourceGraph, size)
        optimized = make_graph(OptimizedResourceGraph, size)

        # Measure the same operations on both implementations.
        # Each entry contains the original time, optimized time, and unit.
        operations = {
            "build": (
                measure_build(ResourceGraph, size),
                measure_build(OptimizedResourceGraph, size),
                "ms"
            ),
            "find_node": (
                measure_call(lambda: baseline.find_node(str(size // 2))),
                measure_call(lambda: optimized.find_node(str(size // 2))),
                "ms"
            ),
            "bfs": (
                measure_call(lambda: baseline.bfs("0")),
                measure_call(lambda: optimized.bfs("0")),
                "ms"
            ),
            "dfs": (
                measure_call(lambda: baseline.dfs("0")),
                measure_call(lambda: optimized.dfs("0")),
                "ms"
            ),
            "remove_node": (
                measure_delete(ResourceGraph, size),
                measure_delete(OptimizedResourceGraph, size),
                "ms"
            ),
            "peak_build_memory": (
                peak_memory(ResourceGraph, size),
                peak_memory(OptimizedResourceGraph, size),
                "MiB"
            ),
        }

        for operation, (old, new, unit) in operations.items():
            # A ratio above 1 means the optimized implementation used
            # less time or memory. A ratio below 1 means it used more.
            ratio = round(old / new, 3) if new else ""

            rows.append({
                "vertices": size,
                "edges": 3 * size - 6,
                "operation": operation,
                "baseline": round(old, 6),
                "optimized": round(new, 6),
                "unit": unit,
                "baseline_over_optimized": ratio
            })

    # Save all measurements so they can be reviewed and plotted later.
    path = RESULTS / "benchmark_results.csv"

    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    # Record the environment because benchmark timings depend on the machine.
    metadata = (
        f"Python: {sys.version.split()[0]}\n"
        f"Platform: {platform.platform()}\n"
        f"Vertices: {SIZES}\n"
        f"Trials: {TRIALS} timing trials (build: 5)\n"
        "Sparse directed graph: each vertex connects to up to three successors.\n"
        "All values are measured locally; timings are environment-dependent.\n"
    )

    (RESULTS / "environment.txt").write_text(metadata)

    print(metadata)
    print(f"Wrote {path}")

    # Print the deletion results because this is the main Phase 3 optimization.
    for row in rows:
        if row["operation"] == "remove_node":
            print(
                f"{row['vertices']:>6} nodes: "
                f"baseline {row['baseline']:.4f}ms, "
                f"optimized {row['optimized']:.4f}ms, "
                f"ratio {row['baseline_over_optimized']:.1f}x"
            )

    return rows


if __name__ == "__main__":
    run()
