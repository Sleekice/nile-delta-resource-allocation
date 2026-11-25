"""Phase 2 regression checks plus Phase 3 correctness and stress tests."""
import random
import unittest
from src.resource_graph import ResourceGraph
from src.optimized_graph import OptimizedResourceGraph


def sample_graph(graph_type):
    graph = graph_type()
    for node_id, kind in [("R", "reservoir"), ("A", "canal"), ("B", "canal"), ("F", "farm"), ("X", "farm")]:
        graph.add_node(node_id, node_id, kind)
    for start, end, capacity in [("R", "A", 100), ("R", "B", 80), ("A", "F", 60), ("B", "F", 40)]:
        graph.add_edge(start, end, capacity)
    return graph


class TestPhase2Compatibility(unittest.TestCase):
    def test_bfs_dfs_and_capacity_equal_to_original(self):
        before = sample_graph(ResourceGraph)
        after = sample_graph(OptimizedResourceGraph)
        for method in ("bfs", "dfs"):
            self.assertEqual(getattr(before, method)("R"), getattr(after, method)("R"))
        for qty in (1, 50, 80, 101):
            self.assertEqual(before.route_has_capacity(["R", "A", "F"], qty), after.route_has_capacity(["R", "A", "F"], qty))

    def test_node_removal_behaves_the_same(self):
        before, after = sample_graph(ResourceGraph), sample_graph(OptimizedResourceGraph)
        before.remove_node("F")
        after.remove_node("F")
        self.assertEqual(before.nodes, after.nodes)
        self.assertEqual(before.adjacency, after.adjacency)
        self.assertTrue(after.check_index())

    def test_duplicate_and_invalid_capacity_do_not_mutate_index(self):
        graph = sample_graph(OptimizedResourceGraph)
        for cap in (0, -1, float("nan"), float("inf"), True):
            with self.assertRaises(ValueError):
                graph.add_edge("A", "B", cap)
        with self.assertRaises(ValueError):
            graph.add_edge("R", "A", 5)
        self.assertTrue(graph.check_index())

    def test_unknown_node_and_edge(self):
        graph = sample_graph(OptimizedResourceGraph)
        with self.assertRaises(KeyError):
            graph.remove_node("missing")
        with self.assertRaises(KeyError):
            graph.remove_edge("A", "B")
        self.assertTrue(graph.check_index())

    def test_cycles_and_disconnected(self):
        graph = sample_graph(OptimizedResourceGraph)
        graph.add_edge("F", "R", 10)
        self.assertEqual(set(graph.bfs("R")), {"R", "A", "B", "F"})
        self.assertIsNone(graph.shortest_feasible_route("R", "X", 1))
        self.assertTrue(graph.check_index())


class TestPhase3Routes(unittest.TestCase):
    def test_shortest_feasible_route_filters_weak_edges(self):
        graph = sample_graph(OptimizedResourceGraph)
        self.assertEqual(graph.shortest_feasible_route("R", "F", 50), ["R", "A", "F"])
        self.assertIsNone(graph.shortest_feasible_route("R", "F", 61))

    def test_widest_path_finds_bottleneck_optimum(self):
        graph = sample_graph(OptimizedResourceGraph)
        self.assertEqual(graph.widest_path("R", "F"), (["R", "A", "F"], 60.0))
        self.assertIsNone(graph.widest_path("F", "R"))

    def test_route_same_node_and_invalid_quantity(self):
        graph = sample_graph(OptimizedResourceGraph)
        self.assertEqual(graph.shortest_feasible_route("A", "A", 10), ["A"])
        self.assertEqual(graph.widest_path("A", "A")[0], ["A"])
        with self.assertRaises(ValueError):
            graph.shortest_feasible_route("R", "F", float("nan"))

    def test_incoming_and_outgoing_maintenance(self):
        graph = sample_graph(OptimizedResourceGraph)
        graph.remove_edge("A", "F")
        self.assertNotIn("A", graph.incoming["F"])
        graph.add_edge("A", "F", 55)
        graph.remove_node("A")
        self.assertNotIn("A", graph.incoming["F"])
        self.assertNotIn("A", graph.adjacency["R"])
        self.assertTrue(graph.check_index())

    def test_high_degree_hub(self):
        graph = OptimizedResourceGraph()
        graph.add_node("hub", "hub", "canal")
        for i in range(300):
            key = f"v{i}"
            graph.add_node(key, key, "farm")
            graph.add_edge("hub", key, 10)
            graph.add_edge(key, "hub", 10)
        graph.remove_node("hub")
        self.assertTrue(graph.check_index())
        self.assertTrue(all(not d for d in graph.adjacency.values()))

    def test_randomized_mutation_matches_baseline(self):
        rng = random.Random(2026)
        baseline, optimized = ResourceGraph(), OptimizedResourceGraph()
        for i in range(180):
            node = str(i)
            baseline.add_node(node, node, "canal")
            optimized.add_node(node, node, "canal")
        existing = set()
        for _ in range(900):
            a, b = rng.sample(range(180), 2)
            pair = (str(a), str(b))
            if pair not in existing:
                baseline.add_edge(*pair, 8)
                optimized.add_edge(*pair, 8)
                existing.add(pair)
        for a, b in rng.sample(sorted(existing), 150):
            baseline.remove_edge(a, b)
            optimized.remove_edge(a, b)
            self.assertTrue(optimized.check_index())
        for node in rng.sample(range(180), 35):
            baseline.remove_node(str(node))
            optimized.remove_node(str(node))
            self.assertTrue(optimized.check_index())
        self.assertEqual(baseline.nodes, optimized.nodes)
        self.assertEqual(baseline.adjacency, optimized.adjacency)

    def test_large_sparse_graph_stress(self):
        graph = OptimizedResourceGraph()
        n = 12000
        for i in range(n):
            graph.add_node(str(i), str(i), "canal")
        for i in range(n - 1):
            graph.add_edge(str(i), str(i + 1), 10)
        self.assertTrue(graph.check_index())
        self.assertEqual(len(graph.bfs("0")), n)
        self.assertEqual(len(graph.dfs("0")), n)
        self.assertEqual(graph.shortest_feasible_route("0", "2", 5), ["0", "1", "2"])
        # Remove the middle of a long chain; reachability should change.
        graph.remove_node(str(n // 2))
        self.assertTrue(graph.check_index())
        self.assertFalse(graph.is_reachable("0", str(n - 1)))


if __name__ == "__main__":
    unittest.main()
