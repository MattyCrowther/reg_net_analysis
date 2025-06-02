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


    def test_node_adaptive(self):
        self.visualiser.set_view()
        pre_elements = self.visualiser.get_view_elements()
        elements = self.visualiser.add_node_shape(pre_elements,shape_type="adaptive")
        self.assertEqual(len(pre_elements),len(elements))
        for e in elements:
            if not self.visualiser._node_shape_handler._is_node(e):
                continue
            for shape in self.visualiser._node_shape_handler.shapes:
                if shape in e["classes"]:
                    break
            else:
                self.fail()