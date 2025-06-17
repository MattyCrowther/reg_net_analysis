import os
import sys
import unittest

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
from app.tools.visualiser.visual.visual import NetVisVisual
from app.storage.storage_strategies.neo4j.storage import Neo4jStorage
from app.model.model import model
TEST_NEO4J_URI = os.getenv("TEST_NEO4J_URI", "bolt://localhost:7687")
TEST_NEO4J_USER = os.getenv("TEST_NEO4J_USER", "neo4j")
TEST_NEO4J_PASSWORD = os.getenv("TEST_NEO4J_PASSWORD", "Radeon12300")

class TestColourHandler(unittest.TestCase):
    def setUp(self):
        self.handler = Neo4jStorage(TEST_NEO4J_URI,
                                    TEST_NEO4J_USER,
                                    TEST_NEO4J_PASSWORD)
        self.visualiser = NetVisVisual(self.handler)

    def test_node_type(self):
        self.visualiser.set_view()
        pre_elements = self.visualiser.get_view_elements()
        elements = self.visualiser.add_node_colour(pre_elements,
                                                   colour_type="type")
        stylesheet = self.visualiser.get_style()
        self.assertEqual(len(pre_elements),len(elements))
        all_classes = [str(n).split("/")[-1] for n in model.get_classes()]
        for e in elements:
            class_type =  e["classes"]
            if not self.visualiser._node_colour_handler._is_node(e):
                continue
            if any(item in class_type for item in all_classes):
                continue
            if "no_type" in class_type:
                continue
            else:
                self.fail()
        
        for style in stylesheet:
            # Hacky and cheap.
            if "background-color" not in style["style"]:
                continue
            if style["selector"] == ":selected":
                continue
            style_norm =  style["selector"].replace("http_//", "http://")
            if any(item in style_norm for item in all_classes):
                break
            if "no_type" in style["selector"]:
                break
            else:
                self.fail()

    def test_edge_type(self):
        self.visualiser.set_view()
        pre_elements = self.visualiser.get_view_elements()
        elements = self.visualiser.add_edge_colour(pre_elements,
                                                   colour_type="type")
        stylesheet = self.visualiser.get_style()
        self.assertEqual(len(pre_elements),len(elements))
        all_relationships = [str(n).split("/")[-1] 
                             for n in model.get_relationships()]
        for e in elements:
            rel_type =  e["classes"]
            if self.visualiser._node_colour_handler._is_node(e):
                continue
            elif any(item in rel_type for item in all_relationships):
                continue
            else:
                self.fail()
        
        for style in stylesheet:
            # Hacky and cheap.
            if "line-color" not in style["style"]:
                continue
            if style["selector"] == ":selected":
                continue
            style_norm =  style["selector"].replace("http_//", "http://")
            if any(item in style_norm for item in all_relationships):
                continue
            else:
                self.fail()