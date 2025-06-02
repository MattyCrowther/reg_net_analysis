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



    def test_colour_overwrite(self):
        self.visualiser.set_view()
        pre_elements = self.visualiser.get_view_elements()
        elements1 = self.visualiser.add_node_colour(pre_elements,
                                                   colour_type="standard")
        elements2 = self.visualiser.add_node_colour(pre_elements,
                                                   colour_type="type")
        stylesheet = self.visualiser.get_style()
        for e in elements2:
            self.assertNotIn("standard",e["classes"])

        for selector in stylesheet:
            self.assertNotIn("standard",selector["selector"])

    def test_node_standard(self):
        self.visualiser.set_view()
        pre_elements = self.visualiser.get_view_elements()
        elements = self.visualiser.add_node_colour(pre_elements,
                                                   colour_type="standard")
        stylesheet = self.visualiser.get_style()
        self.assertEqual(len(pre_elements),len(elements))
        for e in elements:
            if not self.visualiser._node_colour_handler._is_node(e):
                continue
            self.assertIn("standard",e["classes"])
        
        for style in stylesheet:
            if style["selector"] == ".node_colour_standard":
                break
        else:
            self.fail()



    def test_edge_standard(self):
        self.visualiser.set_view()
        pre_elements = self.visualiser.get_view_elements()
        elements = self.visualiser.add_edge_colour(pre_elements,
                                                   colour_type="standard")
        stylesheet = self.visualiser.get_style()
        self.assertEqual(len(pre_elements),len(elements))
        for e in elements:
            if self.visualiser._node_colour_handler._is_node(e):
                continue
            self.assertIn("standard",e["classes"])
        
        for style in stylesheet:
            if style["selector"] == ".edge_colour_standard":
                break
        else:
            self.fail()

    def test_edge_colour_overwrite(self):
        self.visualiser.set_view()
        pre_elements = self.visualiser.get_view_elements()
        elements1 = self.visualiser.add_edge_colour(pre_elements,
                                                   colour_type="standard")
        elements2 = self.visualiser.add_edge_colour(pre_elements,
                                                   colour_type="type")
        stylesheet = self.visualiser.get_style()
        for e in elements2:
            self.assertNotIn("standard",e["classes"])

        for selector in stylesheet:
            self.assertNotIn("standard",selector["selector"])