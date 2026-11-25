"""The 13 original Phase 2 tests, retained to verify regression behavior."""
import unittest
from src.resource_graph import ResourceGraph


class TestResourceGraph(unittest.TestCase):
    def setUp(self):
        self.g = ResourceGraph()
        for node_id, kind in [("R", "reservoir"), ("A", "canal"), ("B", "canal"), ("F", "farm"), ("X", "farm")]:
            self.g.add_node(node_id, node_id, kind)
        self.g.add_edge("R", "A", 100)
        self.g.add_edge("R", "B", 80)
        self.g.add_edge("A", "F", 60)
        self.g.add_edge("B", "F", 40)

    def test_find_node_and_missing(self):
        self.assertEqual(self.g.find_node("F").kind, "farm")
        self.assertIsNone(self.g.find_node("missing"))

    def test_duplicate_node(self):
        with self.assertRaises(ValueError):
            self.g.add_node("R", "Again", "reservoir")

    def test_invalid_node(self):
        with self.assertRaises(ValueError):
            self.g.add_node("", "Blank", "farm")
        with self.assertRaises(ValueError):
            self.g.add_node("C", "City", "city")

    def test_missing_endpoint(self):
        with self.assertRaises(KeyError):
            self.g.add_edge("R", "missing", 10)

    def test_invalid_capacity(self):
        for capacity in (0, -1, float("inf"), float("nan"), True):
            with self.subTest(capacity=capacity), self.assertRaises(ValueError):
                self.g.add_edge("A", "B", capacity)

    def test_duplicate_edge_and_self_loop(self):
        with self.assertRaises(ValueError):
            self.g.add_edge("R", "A", 10)
        with self.assertRaises(ValueError):
            self.g.add_edge("R", "R", 10)

    def test_bfs_dfs_and_disconnected(self):
        self.assertEqual(self.g.bfs("R"), ["R", "A", "B", "F"])
        self.assertEqual(self.g.dfs("R"), ["R", "A", "F", "B"])
        self.assertNotIn("X", self.g.bfs("R"))

    def test_cycle_terminates(self):
        self.g.add_edge("F", "R", 10)
        self.assertEqual(set(self.g.bfs("R")), {"R", "A", "B", "F"})
        self.assertEqual(set(self.g.dfs("R")), {"R", "A", "B", "F"})

    def test_direction_matters(self):
        self.assertTrue(self.g.is_reachable("R", "F"))
        self.assertFalse(self.g.is_reachable("F", "R"))

    def test_capacity_validation(self):
        self.assertTrue(self.g.route_has_capacity(["R", "A", "F"], 50))
        self.assertFalse(self.g.route_has_capacity(["R", "B", "F"], 50))
        self.assertFalse(self.g.route_has_capacity(["R", "F"], 1))
        with self.assertRaises(ValueError):
            self.g.route_has_capacity(["R", "A"], -1)
        with self.assertRaises(ValueError):
            self.g.route_has_capacity(["R"], 1)

    def test_remove_edge(self):
        self.g.remove_edge("A", "F")
        self.assertNotIn("F", self.g.neighbors("A"))
        with self.assertRaises(KeyError):
            self.g.remove_edge("A", "F")

    def test_remove_node_removes_incoming_edges(self):
        self.g.remove_node("F")
        self.assertIsNone(self.g.find_node("F"))
        self.assertNotIn("F", self.g.neighbors("A"))
        self.assertNotIn("F", self.g.neighbors("B"))

    def test_empty_graph(self):
        empty = ResourceGraph()
        self.assertEqual(empty.nodes, {})
        with self.assertRaises(KeyError):
            empty.bfs("R")


if __name__ == "__main__":
    unittest.main()
