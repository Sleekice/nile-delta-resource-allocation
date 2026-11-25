
"""
Nile Delta Resource Allocation - Phase 2 Baseline Graph

Author: Peter Nwochie Tiewah
Institution: University of the Cumberlands
Course: MSCS 532 - Algorithms and Data Structures
Instructor: Dr. Michael Solomon
Project: Phase 2 - Proof of Concept
Date: November 2026

Description:
    This module contains the original directed graph implementation
    developed for the Nile Delta water-distribution project.

    The graph represents reservoirs, canals, and farms as nodes.
    Directed edges represent connections between these locations,
    with each edge storing a maximum capacity value.

    Python dictionaries are used to store nodes and their outgoing
    connections. Breadth-first search and depth-first search are
    provided for exploring the network.

    This implementation is retained as the Phase 2 baseline for
    comparison with the optimized graph introduced in Phase 3.

Main Features:
    - Add, find, and remove nodes.
    - Add and remove directed edges.
    - Retrieve outgoing neighbors.
    - Traverse the network using BFS and DFS.
    - Check whether a destination is reachable.
    - Validate the static capacity of a specified route.

Limitations:
    This is a simplified graph model. It does not simulate actual
    water movement, reserve water, or calculate total network flow.

    Node deletion requires scanning the graph's adjacency records
    to remove incoming connections. Phase 3 addresses this
    performance limitation using reverse-adjacency indexing.
"""

from collections import deque
from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Node:
    """
    Represent a location in the water-distribution network.

    A dataclass automatically creates an initializer and useful
    methods such as __repr__ and __eq__, reducing the amount
    of repetitive code needed to represent graph data.

    Attributes:
        node_id: Unique identifier used to locate the node.
        name: Descriptive name of the location.
        kind: Type of location (reservoir, canal, or farm).

    The frozen=True option prevents these values from being
    reassigned after the Node object has been created.
    """

    node_id: str
    name: str
    kind: str


@dataclass(frozen=True)
class Edge:
    """
    Represent a directed connection between two nodes.

    Each edge identifies where a connection begins, where it ends,
    and the maximum capacity assigned to that connection.

    Attributes:
        source: Identifier of the starting node.
        destination: Identifier of the receiving node.
        capacity: Positive numeric capacity of the connection.

    The frozen=True option makes the stored edge values immutable.
    Changes to a connection are handled through graph operations
    rather than by directly modifying an Edge object's fields.
    """

    source: str
    destination: str
    capacity: float


class ResourceGraph:
    """
    Manage a directed graph using dictionaries and adjacency lists.

    The nodes dictionary provides fast access to stored Node objects.
    The adjacency dictionary associates each node with its outgoing
    connections and the corresponding Edge objects.

    This class provides the original Phase 2 behavior and serves
    as the baseline for Phase 3 performance measurements.
    """

    # Only these three location types are supported by the model.
    VALID_KINDS = frozenset({"reservoir", "canal", "farm"})

    def __init__(self):
        """Create empty dictionaries for nodes and outgoing connections."""

        # Store each Node object under its unique identifier.
        self.nodes: dict[str, Node] = {}

        # Each node maps to a dictionary of its outgoing edges.
        self.adjacency: dict[str, dict[str, Edge]] = {}

    def add_node(self, node_id: str, name: str, kind: str) -> None:
        """Validate and add a new node to the graph."""

        # Node identifiers and names must contain meaningful text.
        if not isinstance(node_id, str) or not node_id.strip():
            raise ValueError("node_id must be a nonempty string")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a nonempty string")

        # Reject location types that are not part of this model.
        if kind not in self.VALID_KINDS:
            raise ValueError(
                f"kind must be one of {sorted(self.VALID_KINDS)}"
            )

        # Each identifier must refer to only one node.
        if node_id in self.nodes:
            raise ValueError(f"duplicate node: {node_id}")

        # Store the node and initialize its outgoing connections.
        self.nodes[node_id] = Node(node_id, name, kind)
        self.adjacency[node_id] = {}

    def find_node(self, node_id: str) -> Node | None:
        """
        Find a node using its identifier.

        Returns the Node object if it exists, or None otherwise.
        Dictionary lookup takes expected O(1) time.
        """

        return self.nodes.get(node_id)

    def remove_node(self, node_id: str) -> None:
        """
        Remove a node and all edges connected to it.

        The method removes the node's outgoing connections first,
        then scans the remaining adjacency dictionaries to remove
        edges directed toward the deleted node.

        This graph-wide scan is the main performance limitation
        addressed by the Phase 3 optimized implementation.
        """

        # Make sure the requested node exists before deleting anything.
        self._require_node(node_id)

        # Remove the node and all edges originating from it.
        del self.nodes[node_id]
        del self.adjacency[node_id]

        # Other nodes may still contain edges pointing to the deleted node.
        # We must examine every remaining adjacency dictionary to find them.
        for neighbors in self.adjacency.values():
            neighbors.pop(node_id, None)

    def _require_node(self, node_id: str) -> None:
        """
        Verify that a node exists before performing an operation.

        Raises KeyError if the identifier is not in the graph.
        """

        if node_id not in self.nodes:
            raise KeyError(f"unknown node: {node_id}")

    def add_edge(
        self,
        source: str,
        destination: str,
        capacity: float
    ) -> None:
        """Create a directed edge between two existing nodes."""

        # Both endpoints must exist before they can be connected.
        self._require_node(source)
        self._require_node(destination)

        # Connections from a node back to itself are not supported.
        if source == destination:
            raise ValueError("self-loops are not supported in this PoC")

        # Capacity must be positive and finite.
        # Boolean values are excluded because Python treats them as integers.
        if (
            isinstance(capacity, bool)
            or not isinstance(capacity, (int, float))
            or not isfinite(capacity)
            or capacity <= 0
        ):
            raise ValueError("capacity must be a finite positive number")

        # Prevent duplicate directed connections.
        if destination in self.adjacency[source]:
            raise ValueError(f"duplicate edge: {source} -> {destination}")

        # Store the Edge object under the source node's adjacency dictionary.
        self.adjacency[source][destination] = Edge(
            source,
            destination,
            float(capacity)
        )

    def remove_edge(self, source: str, destination: str) -> None:
        """Remove an existing directed edge from the graph."""

        self._require_node(source)
        self._require_node(destination)

        # Only an existing connection can be removed.
        if destination not in self.adjacency[source]:
            raise KeyError(
                f"edge does not exist: {source} -> {destination}"
            )

        del self.adjacency[source][destination]

    def neighbors(self, node_id: str) -> list[str]:
        """Return the identifiers of nodes directly reachable from a node."""

        self._require_node(node_id)

        # Dictionary keys represent the destinations of outgoing edges.
        return list(self.adjacency[node_id])

    def bfs(self, start: str) -> list[str]:
        """
        Traverse reachable nodes using breadth-first search.

        BFS uses a first-in, first-out queue to visit nearby nodes
        before exploring nodes farther away.

        Returns the node identifiers in traversal order.
        Time complexity is O(V + E) for the reachable graph.
        """

        self._require_node(start)

        # Mark the starting node as visited before adding it to the queue.
        visited = {start}
        queue = deque([start])
        order = []

        while queue:
            # Process the node that has waited longest in the queue.
            current = queue.popleft()
            order.append(current)

            # Add unvisited outgoing neighbors to the queue.
            for neighbor in self.adjacency[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return order

    def dfs(self, start: str) -> list[str]:
        """
        Traverse reachable nodes using depth-first search.

        DFS uses a last-in, first-out stack to explore a path
        before returning to examine other branches.

        An explicit stack avoids the recursion-depth limitations
        of a recursive DFS implementation.

        Returns the node identifiers in traversal order.
        Time complexity is O(V + E) for the reachable graph.
        """

        self._require_node(start)

        visited = set()
        stack = [start]
        order = []

        while stack:
            # Take the most recently added node from the stack.
            current = stack.pop()

            # A node may appear in the stack more than once.
            if current in visited:
                continue

            visited.add(current)
            order.append(current)

            # Reverse neighbor order so earlier inserted neighbors
            # are explored first when popped from the stack.
            stack.extend(reversed(list(self.adjacency[current])))

        return order

    def is_reachable(self, source: str, destination: str) -> bool:
        """
        Determine whether a directed path exists between two nodes.

        Uses BFS to explore the nodes reachable from the source.
        Returns True if the destination is reached, otherwise False.
        """

        self._require_node(destination)

        return destination in self.bfs(source)

    def route_has_capacity(
        self,
        route: list[str],
        quantity: float
    ) -> bool:
        """
        Check whether a specified route supports a requested quantity.

        Every consecutive pair of nodes must have a directed edge
        with capacity greater than or equal to the requested quantity.

        Returns True when the entire route satisfies this condition,
        or False when an edge is missing or has insufficient capacity.

        This method only checks fixed edge capacities. It does not
        reserve water or account for previous allocations.
        """

        # A route needs at least two nodes to contain a connection.
        if len(route) < 2:
            raise ValueError("route must include at least two nodes")

        # Reject invalid quantities before checking the route.
        if (
            isinstance(quantity, bool)
            or not isinstance(quantity, (int, float))
            or not isfinite(quantity)
            or quantity <= 0
        ):
            raise ValueError("quantity must be a finite positive number")

        # Confirm that every node listed in the route exists.
        for node_id in route:
            self._require_node(node_id)

        # zip pairs each node with the next node in the route.
        # For example, [R, A, F] produces (R, A) and (A, F).
        for source, destination in zip(route, route[1:]):

            # Look for the directed edge connecting this pair.
            edge = self.adjacency[source].get(destination)

            # The route fails if a connection is missing or too small.
            if edge is None or edge.capacity < quantity:
                return False

        # Every connection supports the requested quantity.
        return True
