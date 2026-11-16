"""A small, directed, capacity-aware water distribution graph.

This is an educational proof of concept, not a hydraulic simulation.
"""
from collections import deque
from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Node:
    node_id: str
    name: str
    kind: str  # reservoir, canal, or farm


@dataclass(frozen=True)
class Edge:
    source: str
    destination: str
    capacity: float


class ResourceGraph:
    """Maintain an adjacency-list graph with dictionary-based node lookup."""

    VALID_KINDS = frozenset({"reservoir", "canal", "farm"})

    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self.adjacency: dict[str, dict[str, Edge]] = {}

    def add_node(self, node_id: str, name: str, kind: str) -> None:
        if not isinstance(node_id, str) or not node_id.strip():
            raise ValueError("node_id must be a nonempty string")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a nonempty string")
        if kind not in self.VALID_KINDS:
            raise ValueError(f"kind must be one of {sorted(self.VALID_KINDS)}")
        if node_id in self.nodes:
            raise ValueError(f"duplicate node: {node_id}")
        self.nodes[node_id] = Node(node_id, name, kind)
        self.adjacency[node_id] = {}

    def find_node(self, node_id: str) -> Node | None:
        return self.nodes.get(node_id)

    def remove_node(self, node_id: str) -> None:
        self._require_node(node_id)
        del self.nodes[node_id]
        del self.adjacency[node_id]  # outgoing edges
        for neighbors in self.adjacency.values():
            neighbors.pop(node_id, None)  # incoming edges

    def _require_node(self, node_id: str) -> None:
        if node_id not in self.nodes:
            raise KeyError(f"unknown node: {node_id}")

    def add_edge(self, source: str, destination: str, capacity: float) -> None:
        self._require_node(source)
        self._require_node(destination)
        if source == destination:
            raise ValueError("self-loops are not supported in this PoC")
        if isinstance(capacity, bool) or not isinstance(capacity, (int, float)) or not isfinite(capacity) or capacity <= 0:
            raise ValueError("capacity must be a finite positive number")
        if destination in self.adjacency[source]:
            raise ValueError(f"duplicate edge: {source} -> {destination}")
        self.adjacency[source][destination] = Edge(source, destination, float(capacity))

    def remove_edge(self, source: str, destination: str) -> None:
        self._require_node(source)
        self._require_node(destination)
        if destination not in self.adjacency[source]:
            raise KeyError(f"edge does not exist: {source} -> {destination}")
        del self.adjacency[source][destination]

    def neighbors(self, node_id: str) -> list[str]:
        self._require_node(node_id)
        return list(self.adjacency[node_id])

    def bfs(self, start: str) -> list[str]:
        """Visit reachable nodes in breadth-first order using a FIFO queue."""
        self._require_node(start)
        visited = {start}
        queue = deque([start])
        order = []
        while queue:
            current = queue.popleft()
            order.append(current)
            for neighbor in self.adjacency[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return order

    def dfs(self, start: str) -> list[str]:
        """Visit reachable nodes using an explicit LIFO stack."""
        self._require_node(start)
        visited = set()
        stack = [start]
        order = []
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            order.append(current)
            # Reverse to visit the first inserted neighbor first.
            stack.extend(reversed(list(self.adjacency[current])))
        return order

    def is_reachable(self, source: str, destination: str) -> bool:
        self._require_node(destination)
        return destination in self.bfs(source)

    def route_has_capacity(self, route: list[str], quantity: float) -> bool:
        """Check a chosen directed route; does NOT reserve or allocate water."""
        if len(route) < 2:
            raise ValueError("route must include at least two nodes")
        if isinstance(quantity, bool) or not isinstance(quantity, (int, float)) or not isfinite(quantity) or quantity <= 0:
            raise ValueError("quantity must be a finite positive number")
        for node_id in route:
            self._require_node(node_id)
        for source, destination in zip(route, route[1:]):
            edge = self.adjacency[source].get(destination)
            if edge is None or edge.capacity < quantity:
                return False
        return True
