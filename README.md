
# Nile Delta Water-Distribution Graph — Phase 3

**MSCS 532: Algorithms and Data Structures**

### Peter Nwochie Tiewah  


## Overview

This project continues the Nile Delta water-distribution graph developed in Phase 2. It represents reservoirs, canals, and farms as vertices connected by directed edges with capacity values.

Phase 3 focuses on optimizing graph operations, improving scalability, and evaluating performance while preserving the original Phase 2 implementation for comparison.

The project models graph connectivity and static capacity constraints. It is not a physical hydraulic simulation.

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

The new `OptimizedResourceGraph` extends the original graph and introduces:

- Reverse-adjacency indexing for faster node deletion
- Consistency checks for incoming and outgoing edges
- Minimum-hop feasible route searching using BFS
- Widest-path searching using a priority queue
- Additional automated tests and stress testing
- Performance and memory comparisons against Phase 2

The optimized implementation is located in `src/optimized_graph.py`.

## Requirements

- Python 3.10 or later
- Matplotlib for generating performance graphs

The graph implementations, automated tests, and benchmarks use Python's standard library. Matplotlib is only required to generate the visualization.

Install the optional plotting dependency:

```bash
python3 -m pip install -r requirements.txt
```

## Running the Project

Run all commands from the project root.

### 1. Run Automated Tests

```bash
python3 -m unittest discover -s tests -v
```

The project contains 25 automated tests, including 13 original Phase 2 tests and 12 new Phase 3 tests.

All 25 tests passed during local testing.

### 2. Run the Demonstration

```bash
python3 -m examples.demo
```

The demonstration uses a small synthetic water-distribution network to show graph traversal, feasible route searching, widest-path searching, and reverse-index maintenance after node deletion.

### 3. Run Performance Benchmarks

```bash
python3 -m benchmark.benchmark_phase3
```

The benchmark compares the original and optimized implementations using directed graphs containing:

- 1,000 vertices
- 5,000 vertices
- 10,000 vertices
- 20,000 vertices

Each vertex connects to up to three subsequent vertices, creating a sparse directed network.

The benchmark measures:

- Graph construction time
- Node lookup
- BFS traversal
- DFS traversal
- Node deletion
- Peak traced Python memory during construction

Timing results use the median of nine trials, except graph construction, which uses five trials.

The benchmark writes:

- `results/benchmark_results.csv`
- `results/environment.txt`

Rerunning the benchmark overwrites these results and may produce different timings depending on the execution environment.

### 4. Generate the Performance Graph

```bash
python3 -m benchmark.plot_results
```

The plotting script reads `results/benchmark_results.csv` and generates:

`figures/performance_graph.png`

The colored graph compares node-deletion times and displays the speedup achieved by the optimized implementation.

The plotting script does not rerun the benchmark or modify the CSV data.

## Project Structure

```text
nile-delta-resource-allocation/
├── benchmark/
│   ├── __init__.py
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
├── Nile_Delta_Phase_3_Latest_Benchmark.docx
├── .gitignore
├── README.md
└── requirements.txt
```

## Performance Results

Benchmarks were executed using:

- **Python:** 3.15.2
- **Operating system:** macOS 27.0.1
- **Architecture:** ARM64

### Node Deletion Performance

The following table contains median execution times from the final recorded benchmark.

| Vertices | Phase 2 (ms) | Phase 3 (ms) | Speedup |
|---|---:|---:|---:|
| 1,000 | 0.020250 | 0.001250 | 16.2x |
| 5,000 | 0.097041 | 0.001958 | 49.6x |
| 10,000 | 0.208833 | 0.003000 | 69.6x |
| 20,000 | 0.492833 | 0.005458 | 90.3x |

At 20,000 vertices, the original implementation required approximately 0.4928 milliseconds to delete a node, compared with 0.0055 milliseconds for the optimized implementation.

This represents a **90.3x improvement in node-deletion performance** for the tested sparse graph.

The improvement occurs because the optimized graph maintains incoming-edge references. Instead of searching every node for incoming connections, deletion processes only the edges associated with the selected vertex.

### Performance Trade-offs

The optimization introduces additional overhead.

At 20,000 vertices:

| Metric | Phase 2 | Phase 3 |
|---|---:|---:|
| Graph construction | 34.652667 ms | 41.439625 ms |
| Peak traced memory | 20.011086 MiB | 24.526794 MiB |
| BFS traversal | 3.081208 ms | 2.947417 ms |
| DFS traversal | 3.892667 ms | 3.912166 ms |

The optimized implementation required approximately:

- **19.6% more construction time**
- **22.6% more peak traced memory**

BFS and DFS performance remained broadly similar. Their small measured differences do not establish a meaningful traversal improvement.

These results demonstrate a trade-off between faster node deletion and additional memory and construction overhead.

The reported measurements apply to synthetic sparse graphs. Performance may differ for dense graphs, high-degree vertices, other workloads, and different computers.

## Design and Complexity Analysis

Let:

- V = number of vertices
- E = number of directed edges
- d-in = incoming degree of a selected vertex
- d-out = outgoing degree of a selected vertex

Both implementations use dictionaries and adjacency lists requiring O(V + E) storage.

The Phase 3 implementation introduces an additional reverse-adjacency index, which also requires O(V + E) space.

### Time Complexity Comparison

| Operation | Phase 2 | Phase 3 |
|---|---|---|
| Find node | Expected O(1) | Expected O(1) |
| Add edge | Expected O(1) | Expected O(1) |
| Delete node | Expected O(V + d-out) | Expected O(d-in + d-out) |
| BFS | O(V + E) | O(V + E) |
| DFS | O(V + E) | O(V + E) |

The primary improvement occurs during node deletion.

The original implementation scans all remaining adjacency dictionaries to remove incoming references. The optimized implementation stores these incoming references in advance, allowing it to access the affected nodes directly.

Maintaining the additional index introduces extra work during edge insertion and deletion.

## Testing and Validation

The project contains 25 automated tests.

The original Phase 2 tests verify the functionality of the initial graph implementation.

The additional Phase 3 tests examine:

- Compatibility with the original implementation
- Reverse-index consistency
- Node and edge deletion
- Invalid inputs and capacities
- Cycles and disconnected graphs
- High-degree vertices
- Randomized graph modifications
- Capacity-aware route searching
- A 12,000-node stress test

All 25 tests passed on the development machine.

The tests provide evidence that the optimized implementation preserves the expected behavior of Phase 2 while supporting the additional Phase 3 functionality.

## Limitations

This project is an educational graph implementation rather than a complete water-distribution management system.

The current implementation does not:

- Simulate physical water movement
- Reserve or allocate water
- Enforce supply-and-demand balances
- Model pumping costs, water loss, or changing water levels
- Calculate total maximum flow across multiple routes
- Provide persistence or concurrent graph updates

The minimum-hop feasible route minimizes the number of connections rather than geographic distance.

The widest-path algorithm maximizes the minimum capacity along one route. It does not calculate the total flow that could be distributed through the network.

Future development could include actual resource allocation, flow conservation, persistence, concurrency controls, geographic information, and hydraulic modeling.

## Academic Report

The accompanying report, `Nile_Delta_Phase_3_Latest_Benchmark.docx`, documents:

- Phase 2 background and original implementation
- Phase 3 optimization techniques
- Scaling strategy and theoretical complexity
- Advanced testing and validation
- Measured performance comparisons
- Memory and execution-time trade-offs
- Limitations and future improvements

The report includes a performance table, a colored graph, and peer-reviewed academic references.

## GitHub and Development History

**Repository:**  
https://github.com/Sleekice/nile-delta-resource-allocation

**Phase 3 Branch:**  
https://github.com/Sleekice/nile-delta-resource-allocation/tree/phase-3-optimization

Phase 2 established the original proof-of-concept implementation.

Phase 3 extends that work using reverse-adjacency indexing, additional routing algorithms, expanded testing, and performance evaluation.

The original Phase 2 implementation remains available for comparison, and the repository's Git history documents the project's development across both phases.
