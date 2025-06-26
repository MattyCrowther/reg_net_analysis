import os
import sys
import unittest

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
from app.tools.visualiser.visual.net_vis_view_visual import NetVisVisual
from app.storage.storage_strategies.neo4j.storage import Neo4jStorage
from app.model.model import model
TEST_NEO4J_URI = os.getenv("TEST_NEO4J_URI", "bolt://localhost:7687")
TEST_NEO4J_USER = os.getenv("TEST_NEO4J_USER", "neo4j")
TEST_NEO4J_PASSWORD = os.getenv("TEST_NEO4J_PASSWORD", "Radeon12300")

class TestLabelHandler(unittest.TestCase):
    def setUp(self):
        self.handler = Neo4jStorage(TEST_NEO4J_URI,
                                    TEST_NEO4J_USER,
                                    TEST_NEO4J_PASSWORD)
        self.visualiser = NetVisVisual(self.handler)

    def test_node_name(self):
        self.visualiser.set_view()
        view = self.visualiser._builder.view
        pre_elements = self.visualiser.get_view_elements()
        elements = self.visualiser.add_node_labels(pre_elements,label_type="name")
        self.assertEqual(len(pre_elements),len(elements))
        
        for e in elements:
            if not self.visualiser._node_colour_handler._is_node(e):
                continue
            node = view.get_node(e["data"]["id"])
            self.assertEqual(e["data"]["label"],node.properties[str(model.identifiers.external.title)][0])

    def test_node_class_type(self):
        self.visualiser.set_view()
        pre_elements = self.visualiser.get_view_elements()
        all_classes = [str(n) for n in model.get_classes()]
        elements = self.visualiser.add_node_labels(pre_elements,label_type="class_type")
        self.assertEqual(len(pre_elements),len(elements))
        for e in elements:
            if not self.visualiser._node_colour_handler._is_node(e):
                continue
            self.assertIn(e["data"]["label"],all_classes)

    def test_edge_class_type(self):
        self.visualiser.set_view()
        pre_elements = self.visualiser.get_view_elements()
        all_relationships = [str(n) for n in model.get_relationships()]
        elements = self.visualiser.add_edge_labels(pre_elements,label_type="relationship_type")
        self.assertEqual(len(pre_elements),len(elements))
        for e in elements:
            if self.visualiser._node_colour_handler._is_node(e):
                continue
            self.assertIn(e["data"]["label"],all_relationships)