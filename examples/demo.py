
"""
Nile Delta Resource Allocation - Phase 3 Demonstration

Author: Peter Nwochie Tiewah
Institution: University of the Cumberlands
Course: MSCS 532 - Algorithms and Data Structures
Instructor: Dr. Michael Solomon
Project: Phase 3 - Optimization, Scaling, and Final Evaluation
Date: November 2026

Description:
    This module demonstrates the functionality of the optimized
    Nile Delta water-distribution graph using a small synthetic network.

    The example contains one reservoir, two canals, and one farm.
    Each directed connection has a capacity representing the maximum
    amount of water that could pass through that connection.

    The demonstration uses the OptimizedResourceGraph introduced in
    Phase 3 and shows how its routing algorithms operate.

Operations Demonstrated:
    - Creating vertices and directed connections
    - Breadth-first search (BFS)
    - Finding a feasible route based on capacity
    - Finding the widest path through the network
    - Removing a vertex and maintaining the reverse-adjacency index
    - Checking how node deletion affects available routes

Purpose:
    The example provides a simple way to observe and verify the
    graph's behavior before evaluating larger networks.

    All capacities and connections are fictional. This is an
    educational graph model, not a physical water-flow simulation.

Usage:
    python3 -m examples.demo
"""

from src.optimized_graph import OptimizedResourceGraph


def main():
    """Build a small water network and demonstrate the graph operations."""

    # Create an instance of the optimized Phase 3 graph.
    graph = OptimizedResourceGraph()

    # Add one reservoir, two canals, and one farm.
    # The node ID is used to identify each location in the network.
    for node_id, kind in [
        ("R", "reservoir"),
        ("A", "canal"),
        ("B", "canal"),
        ("F", "farm")
    ]:
        graph.add_node(node_id, node_id, kind)

    # Add directed connections with their maximum capacities.
    # Water can travel from R to F through either canal A or canal B.
    for start, end, capacity in [
        ("R", "A", 100),
        ("A", "F", 60),
        ("R", "B", 80),
        ("B", "F", 40)
    ]:
        graph.add_edge(start, end, capacity)

    # Visit all reachable nodes starting from the reservoir.
    print("BFS:", graph.bfs("R"))

    # Find a route that supports at least 50 units of capacity.
    # The route through B cannot qualify because B -> F supports only 40.
    print(
        "50-unit feasible route:",
        graph.shortest_feasible_route("R", "F", 50)
    )

    # Find the path with the highest minimum edge capacity.
    # R -> A -> F has a bottleneck of 60, compared with 40 through B.
    print("Widest route:", graph.widest_path("R", "F"))

    # Remove canal A to simulate a change in network connectivity.
    graph.remove_node("A")

    # Check that the reverse-adjacency index remains consistent.
    print("After removing A, index valid:", graph.check_index())

    # Check whether a 50-unit route is still available.
    # Only the route through B remains, and its bottleneck is 40.
    print(
        "After removing A, 50-unit feasible route:",
        graph.shortest_feasible_route("R", "F", 50)
    )


if __name__ == "__main__":
    main()
