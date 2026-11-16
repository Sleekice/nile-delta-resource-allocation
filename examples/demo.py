"""Execute with: python -m examples.demo"""
from src.resource_graph import ResourceGraph


def main() -> None:
    network = ResourceGraph()
    for node_id, name, kind in [
        ("R", "Main Reservoir", "reservoir"),
        ("A", "Canal A", "canal"),
        ("B", "Canal B", "canal"),
        ("F1", "Farm One", "farm"),
        ("F2", "Farm Two", "farm"),
        ("F3", "Farm Three", "farm"),
    ]:
        network.add_node(node_id, name, kind)
    for source, destination, capacity in [
        ("R", "A", 100), ("R", "B", 80),
        ("A", "F1", 70), ("A", "F2", 60),
        ("B", "F2", 50), ("B", "F3", 40),
    ]:
        network.add_edge(source, destination, capacity)

    print("Adjacency:", {node: network.neighbors(node) for node in network.nodes})
    print("Search F2:", network.find_node("F2"))
    print("BFS from R:", network.bfs("R"))
    print("DFS from R:", network.dfs("R"))
    print("R reaches F2:", network.is_reachable("R", "F2"))
    print("Alternate routes to F2:", network.route_has_capacity(["R", "A", "F2"], 45), network.route_has_capacity(["R", "B", "F2"], 45))
    print("R -> B -> F3 supports 50 units:", network.route_has_capacity(["R", "B", "F3"], 50))
    network.remove_edge("B", "F3")
    print("After removing B -> F3, reachable:", network.is_reachable("R", "F3"))
    network.remove_node("F1")
    print("After removing F1, neighbors of A:", network.neighbors("A"))


if __name__ == "__main__":
    main()
