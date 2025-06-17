import os
import sys
import unittest

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..", ".."))
sys.path.insert(0, os.path.join("..", "..", ".."))

from app.storage.storage_strategies.neo4j.storage import Neo4jStorage
from app.tools.utility.graph_analyser import analyse
from app.tools.utility.markdown_generator import generate_markdown

TEST_NEO4J_URI = os.getenv("TEST_NEO4J_URI", "bolt://localhost:7687")
TEST_NEO4J_USER = os.getenv("TEST_NEO4J_USER", "neo4j")
TEST_NEO4J_PASSWORD = os.getenv("TEST_NEO4J_PASSWORD", "Radeon12300")

class TestGraphAnalyser(unittest.TestCase):
    def setUp(self):
        self._handler = Neo4jStorage(
            TEST_NEO4J_URI,
            TEST_NEO4J_USER,
            TEST_NEO4J_PASSWORD
        )

    def test_analyse_returns_expected_structure(self):
        result = analyse(self._handler)
        self.assertIsInstance(result, dict)
        self.assertIn("graph", result)
        self.assertIn("semantic", result)

        graph_metrics = result["graph"]
        semantic_metrics = result["semantic"]

        self.assertIsInstance(graph_metrics, dict)
        self.assertIsInstance(semantic_metrics, dict)

        self.assertIn("description", graph_metrics)
        self.assertIn("description", semantic_metrics)

        # Check that some expected keys exist in each
        expected_graph_keys = [
            "basic_structure", "degree_distribution", "connected_components",
            "shortest_paths", "density", "clustering_coefficient",
            "centrality_metrics", "assortativity", "node_similarity"
        ]
        expected_semantic_keys = [
            "node_label_distribution", "relationship_type_semantics", "sequence_similarity"
        ]

        for key in expected_graph_keys:
            self.assertIn(key, graph_metrics)

        for key in expected_semantic_keys:
            self.assertIn(key, semantic_metrics)

    def test_metrics_format(self):
        result = analyse(self._handler)
        for section in result["graph"].values():
            if isinstance(section, dict):
                self.assertIn("metrics", section)
        for section in result["semantic"].values():
            if isinstance(section, dict):
                self.assertIn("metrics", section)

if __name__ == "__main__":
    unittest.main()
