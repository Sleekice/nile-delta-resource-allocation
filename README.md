
# Nile Delta Water-Distribution Graph — Phase 3

**MSCS 532: Algorithms and Data Structures**

## Overview

This project continues the Nile Delta water-distribution graph developed in Phase 2. It represents reservoirs, canals, and farms as vertices connected by directed edges with capacity values.

Phase 3 focuses on improving performance and scalability while preserving the original implementation for comparison.

The project models graph connectivity and capacity constraints, not a complete physical water-distribution system.

## Phase 2 and Phase 3

### Phase 2: Original Implementation

The original `ResourceGraph` supports:

- Adding, finding, and removing nodes
- Adding and removing directed edges
- Breadth-first search (BFS)
- Depth-first search (DFS)
- Reachability checking
- Route-capacity validation

The original implementation is preserved in `src/resource_graph.py`.

### Phase 3: Optimized Implementation

The new `OptimizedResourceGraph` introduces:

- Reverse-adjacency indexing for faster node deletion
- Consistency checks for incoming and outgoing edges
- Minimum-hop feasible route searching
- Widest-path searching using a priority queue
- Additional automated tests and stress testing
- Performance and memory comparisons against Phase 2

The optimized implementation is located in `src/optimized_graph.py`.

## Requirements

- Python 3.10 or later
- Matplotlib for generating performance graphs

The graph implementations, automated tests, and benchmarks use Python's standard library.

Install the optional plotting dependency:

```bash
python3 -m pip install -r requirements.txt
```

## Running the Project

Run the following commands from the project root.

### 1. Run all tests

```bash
python3 -m unittest discover -s tests -v
```

The project contains 25 automated tests, including the 13 original Phase 2 tests.

### 2. Run the demonstration

```bash
python3 -m examples.demo
```

The demonstration shows graph traversal, feasible route searching, widest-path searching, and index maintenance after node deletion.

### 3. Run performance benchmarks

```bash
python3 -m benchmark.benchmark_phase3
```

The benchmark compares the original and optimized implementations using graphs containing 1,000, 5,000, 10,000, and 20,000 vertices.

It measures:

- Graph construction
- Node lookup
- BFS traversal
- DFS traversal
- Node deletion
- Peak traced memory during construction

The benchmark writes results to:

- `results/benchmark_results.csv`
- `results/environment.txt`

### 4. Generate performance graphs

```bash
python3 -m benchmark.plot_results
```

This script reads the recorded benchmark results and generates a colored comparison graph at:

`figures/performance_graph.png`

The plot distinguishes the original and optimized implementations and displays node-deletion speedups.

## Project Files

```text
nile-delta-resource-allocation/
├── benchmark/
│   ├── benchmark_phase3.py
│   └── plot_results.py
├── examples/
│   └── demo.py
├── figures/
│   └── performance_graph.png
├── results/
│   ├── benchmark_console.txt
│   ├── benchmark_results.csv
│   ├── demo_output.txt
│   ├── environment.txt
│   └── test_output.txt
├── src/
│   ├── __init__.py
│   ├── resource_graph.py
│   └── optimized_graph.py
├── tests/
│   ├── test_phase2_original.py
│   └── test_phase3.py
├── Phase_3_Final_Report.docx
├── README.md
└── requirements.txt
```

## Performance Results

Benchmarks were executed using Python 3.15.2 on macOS 27.0.1 (ARM64).

The results below show median node-deletion execution times.

| Vertices | Phase 2 (ms) | Phase 3 (ms) | Speedup |
|---|---:|---:|---:|
| 1,000 | 0.019709 | 0.001292 | 15.3x |
| 5,000 | 0.099917 | 0.001959 | 51.0x |
| 10,000 | 0.200250 | 0.002750 | 72.8x |
| 20,000 | 0.521708 | 0.005917 | 88.2x |

At 20,000 vertices, the optimized implementation achieved approximately 88.2 times faster node deletion.

However, the optimization introduces additional overhead:

- Graph construction was approximately 22.2% slower.
- Peak traced memory increased approximately 22.6%.
- BFS and DFS performance remained broadly similar.

The results demonstrate that reverse-adjacency indexing can improve node-deletion performance significantly in sparse graphs while requiring additional memory.

Benchmark timings depend on the execution environment and may differ between runs.

## Design and Complexity

Let V represent the number of vertices and E the number of edges.

Both implementations use dictionaries and adjacency lists requiring O(V + E) storage.

The optimized graph introduces an additional incoming-edge index, also requiring O(V + E) space.

### Time Complexity

| Operation | Phase 2 | Phase 3 |
|---|---|---|
| Find node | Expected O(1) | Expected O(1) |
| Add edge | Expected O(1) | Expected O(1) |
| Delete node | Expected O(V + degree) | Expected O(in-degree + out-degree) |
| BFS | O(V + E) | O(V + E) |
| DFS | O(V + E) | O(V + E) |

The main performance improvement occurs during node deletion because the optimized graph no longer needs to scan unrelated vertices.

## Testing and Validation

All 25 automated tests passed during local testing.

Testing includes:

- Original Phase 2 functionality
- Reverse-index consistency
- Node and edge deletion
- Invalid inputs
- Cycles and disconnected graphs
- High-degree vertices
- Randomized graph modifications
- A 12,000-node stress test
- Capacity-aware route searching

## Limitations

This implementation does not simulate physical water movement, allocate water between consumers, or enforce flow conservation.

The minimum-hop route minimizes the number of edges rather than geographic distance.

The widest-path algorithm maximizes the minimum capacity along a single route; it does not calculate maximum total network flow.

Future development could include demand allocation, persistence, real geographic data, concurrency controls, and hydraulic modeling.

## Academic Report

The accompanying `Phase_3_Final_Report.docx` documents the optimization, theoretical complexity, scaling approach, testing, experimental results, trade-offs, and future improvements.

## GitHub and Development History

Repository:

https://github.com/Sleekice/nile-delta-resource-allocation

Phase 2 established the original proof of concept.

Phase 3 continues the same project on the `phase-3-optimization` branch, preserving the original implementation and Git history for comparison.
