# Nile Delta — Phase 2 Proof of Concept

**MSCS 532: Developing and Optimizing Data Structures for Real-World Applications Using Python**

A deliberately small, in-memory proof of concept for a directed water-distribution graph. Reservoirs, canals, and farms are vertices; directed resource connections are edges. Python dictionaries implement node lookup and adjacency lists.

## Run

From the project root, using Python 3.10 or later:

```bash
python -m unittest discover -s tests -v
python -m examples.demo
```

No third-party dependencies are required.

## Implemented

- Add, search, and delete nodes
- Add and delete directed edges with positive, finite capacities
- Breadth-first traversal (queue) and depth-first traversal (stack)
- Directed reachability and explicit-route capacity checks
- Exceptions for invalid input and tests for disconnected nodes, cycles, and deletions

## Intentional limitations

- `route_has_capacity` checks each edge's **static maximum** capacity; it does not allocate, reserve, or track water.
- No supply/demand balances, flow conservation, parallel-flow scheduling, shortest-path or maximum-flow optimization.
- No persistence, concurrency controls, hydraulic simulation, or large-scale benchmarking.
- No claim of real-world production readiness.

## Data-structure costs

Let V be vertices, E edges, d the number of outgoing neighbors, and L route length.

- Dictionary node lookup and adjacency edge insertion: average O(1).
- BFS and DFS: O(V + E) time and O(V) auxiliary space in the worst case.
- Graph storage: O(V + E).
- Capacity validation for an explicit route: O(L).
- Node deletion: O(V) average expected time here (scans all outgoing-neighbor dictionaries to delete incoming edges), plus incident-edge removal.

## Next steps for Phase 3

Evaluate reverse adjacency indexing for faster node deletion, add allocations with flow conservation and rollback semantics, benchmark scale, and explore shortest paths and maximum flow.

## GitHub
https://github.com/Sleekice/nile-delta-resource-allocation
