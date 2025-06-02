import os
import sys
import unittest

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
from app.tools.visualiser.builder.abstract import Builder
from app.tools.visualiser.visual.abstract import Visual
from app.storage.storage_strategies.neo4j.storage import Neo4jStorage

TEST_NEO4J_URI = os.getenv("TEST_NEO4J_URI", "bolt://localhost:7687")
TEST_NEO4J_USER = os.getenv("TEST_NEO4J_USER", "neo4j")
TEST_NEO4J_PASSWORD = os.getenv("TEST_NEO4J_PASSWORD", "Radeon12300")

class TestLabelHandler(unittest.TestCase):
    def setUp(self):
        self.handler = Neo4jStorage(TEST_NEO4J_URI,
                                    TEST_NEO4J_USER,
                                    TEST_NEO4J_PASSWORD)
        self.builder = Builder(self.handler)


    def test_full_view_builder(self):
        view = self.builder.set_view()
        elements = self.builder.get_view_elements()

        nodes = []
        edges = []
        for e in elements:
            if "source" in e["data"]:
                edges.append(e)
            else:
                nodes.append(e["data"]["id"])

        for edge in edges:
            source = edge["data"]["source"]
            target = edge["data"]["target"]
            self.assertIn(source,nodes)
            self.assertIn(target,nodes)