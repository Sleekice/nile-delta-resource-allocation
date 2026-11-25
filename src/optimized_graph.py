
"""
Nile Delta Resource Allocation - Optimized Graph Implementation

Author: Peter Nwochie Tiewah
Institution: University of the Cumberlands
Course: MSCS 532 - Algorithms and Data Structures
Instructor: Dr. Michael Solomon
Project: Phase 3 - Optimization, Scaling, and Final Evaluation
Date: November 2026

Description:
    This module extends the ResourceGraph implementation developed in
    Phase 2 by introducing a reverse-adjacency index.

    The original graph stores outgoing connections for each node.
    The optimized graph also records incoming connections, allowing
    node deletion without searching through every node in the network.

    This improves deletion performance for large, sparsely connected
    graphs while requiring additional memory and index maintenance.

    The module also introduces two routing algorithms:
    - Shortest feasible route using breadth-first search (BFS).
    - Widest path using a priority queue.

    The implementation preserves the public operations from Phase 2
    and adds functionality for evaluating network connectivity and
    capacity constraints.

    This project models a directed water-distribution graph.
    It does not simulate physical water movement or allocate water.
"""

from collections import deque
from heapq import heappop, heappush
from math import inf, isfinite

from src.resource_graph import ResourceGraph


class OptimizedResourceGraph(ResourceGraph):
    """
    Extend the original graph with incoming-edge indexing and route searches.

    The reverse index stores the sources of incoming connections for each
    node. This allows node deletion to process only the affected edges
    instead of scanning the entire graph.
    """

    def __init__(self):
        """Initialize the graph and its reverse-adjacency index."""

        # Initialize the nodes and outgoing edges from the Phase 2 class.
        super().__init__()

        # Each node will have a set containing its incoming neighbors.
        self.incoming: dict[str, set[str]] = {}

    def add_node(self, node_id: str, name: str, kind: str) -> None:
        """Add a node and create an empty set for its incoming connections."""

        # Let the original class validate and insert the node.
        super().add_node(node_id, name, kind)

        # A newly created node does not have any incoming edges.
        self.incoming[node_id] = set()

    def add_edge(
        self,
        source: str,
        destination: str,
        capacity: float
    ) -> None:
        """Add a directed edge and update the reverse index."""

        # Perform the original validation before updating the index.
        super().add_edge(source, destination, capacity)

        # Record the source as an incoming neighbor of the destination.
        self.incoming[destination].add(source)

    def remove_edge(self, source: str, destination: str) -> None:
        """Remove an edge from both the graph and its reverse index."""

        # Remove the original outgoing connection.
        super().remove_edge(source, destination)

        # Remove the matching incoming connection.
        self.incoming[destination].remove(source)

    def remove_node(self, node_id: str) -> None:
        """Delete a node and remove all edges connected to it."""

        # Confirm that the node exists before making changes.
        self._require_node(node_id)

        # Remove references to this node from the destinations it connects to.
        for destination in self.adjacency[node_id]:
            self.incoming[destination].remove(node_id)

        # The reverse index tells us exactly which nodes point to this node.
        # This avoids searching every node in the graph.
        for source in self.incoming[node_id]:
            del self.adjacency[source][node_id]

        # Remove the node and its remaining records.
        del self.incoming[node_id]
        del self.adjacency[node_id]
        del self.nodes[node_id]

    def check_index(self) -> bool:
        """Verify that incoming and outgoing edge records agree."""

        # Every node should appear in both adjacency structures.
        if (
            set(self.incoming) != set(self.nodes)
            or set(self.adjacency) != set(self.nodes)
        ):
            return False

        # Check that every outgoing edge has a matching incoming reference.
        for source, targets in self.adjacency.items():
            for target in targets:
                if (
                    target not in self.incoming
                    or source not in self.incoming[target]
                ):
                    return False

        # Check that every incoming reference points to an existing edge.
        for target, sources in self.incoming.items():
            for source in sources:
                if (
                    source not in self.adjacency
                    or target not in self.adjacency[source]
                ):
                    return False

        return True

    def shortest_feasible_route(
        self,
        source: str,
        destination: str,
        quantity: float
    ) -> list[str] | None:
        """
        Find the route with the fewest edges that supports a given quantity.

        Breadth-first search visits nodes in increasing order of distance
        measured by edge count. Edges with insufficient capacity are skipped.

        Returns a list of node IDs if a route exists, or None otherwise.
        This method checks static capacities without reserving water.
        """

        # Both endpoints must exist in the graph.
        self._require_node(source)
        self._require_node(destination)

        # A requested quantity must be a positive, finite number.
        if (
            isinstance(quantity, bool)
            or not isinstance(quantity, (int, float))
            or not isfinite(quantity)
            or quantity <= 0
        ):
            raise ValueError("quantity must be a finite positive number")

        # If both endpoints are the same, no edges need to be traversed.
        if source == destination:
            return [source]

        # Track how each node was reached so the route can be reconstructed.
        parent = {source: None}
        queue = deque([source])

        while queue:
            current = queue.popleft()

            for neighbor, edge in self.adjacency[current].items():

                # Skip connections that cannot support the requested quantity.
                # Also skip nodes already discovered by the search.
                if edge.capacity < quantity or neighbor in parent:
                    continue

                parent[neighbor] = current

                # Once the destination is found, trace the route backward.
                if neighbor == destination:
                    route = [destination]

                    while parent[route[-1]] is not None:
                        route.append(parent[route[-1]])

                    # Reverse the collected nodes to return source to destination.
                    return list(reversed(route))

                queue.append(neighbor)

        # No route meets the requested capacity.
        return None

    def widest_path(
        self,
        source: str,
        destination: str
    ) -> tuple[list[str], float] | None:
        """
        Find a route with the greatest possible bottleneck capacity.

        The bottleneck is the smallest edge capacity along a route.
        This algorithm selects the route whose bottleneck is largest.

        A priority queue processes routes with higher bottleneck
        capacities before routes with lower capacities.

        Returns the route and its bottleneck capacity, or None if
        the destination cannot be reached.

        This is a static capacity calculation, not water allocation.
        """

        self._require_node(source)
        self._require_node(destination)

        # A route from a node to itself contains no limiting edges.
        if source == destination:
            return ([source], inf)

        # Store the best bottleneck capacity found for each node.
        best = {source: inf}

        # Keep track of the preceding node for route reconstruction.
        parent = {source: None}

        # Python uses a min-heap, so negative values prioritize larger widths.
        heap = [(-inf, source)]

        while heap:
            negative_width, current = heappop(heap)
            width = -negative_width

            # Ignore entries that are no longer the best route to this node.
            if width < best[current]:
                continue

            # The destination has been reached with its best bottleneck.
            if current == destination:
                route = [destination]

                while parent[route[-1]] is not None:
                    route.append(parent[route[-1]])

                return list(reversed(route)), width

            for neighbor, edge in self.adjacency[current].items():

                # A route can only carry as much as its weakest connection.
                candidate = min(width, edge.capacity)

                # Update the route if it provides a better bottleneck.
                if candidate > best.get(neighbor, -1):
                    best[neighbor] = candidate
                    parent[neighbor] = current

                    # Add the improved route to the priority queue.
                    heappush(heap, (-candidate, neighbor))

        # Return None when the destination is unreachable.
        return None
