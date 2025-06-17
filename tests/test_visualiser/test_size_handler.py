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
        builder = Builder(self.handler)
        self.visualiser = Visual(builder)
        self._standard_size = self.visualiser._size_handler._standard_node_size



    def test_node_standard(self):
        self.visualiser.set_view()
        pre_elements = self.visualiser.get_view_elements()
        elements = self.visualiser.add_node_size(pre_elements,size_type="standard")
        self.assertEqual(len(pre_elements),len(elements))
        for e in elements:
            if not self.visualiser._size_handler._is_node(e):
                continue
            self.assertEqual(e["data"]["size"],self._standard_size)

    def test_node_type(self):
        self.visualiser.set_view()
        pre_elements = self.visualiser.get_view_elements()
        elements = self.visualiser.add_node_size(pre_elements,size_type="type")
        self.assertEqual(len(pre_elements),len(elements))
        for e in elements:
            if not self.visualiser._size_handler._is_node(e):
                continue
            n_id = e["data"]["id"]
            node = self.visualiser._builder.view.get_node(n_id)
            node_type = node.type
            if node_type is None:
                self.assertEqual(e["data"]["size"],self._standard_size/2)
            else:
                self.assertEqual(e["data"]["size"],self._standard_size)

    def test_node_centrality(self):
        self.visualiser.set_view()
        pre_elements = self.visualiser.get_view_elements()
        elements = self.visualiser.add_node_size(pre_elements,size_type="centrality")
        self.assertEqual(len(pre_elements),len(elements))