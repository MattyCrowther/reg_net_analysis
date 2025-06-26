import os
import sys
import unittest

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
from app.tools.visualiser.visual.net_vis_explore_visual import NetVisExploreVisual
from app.storage.storage_strategies.neo4j.storage import Neo4jStorage
from app.model.model import model

TEST_NEO4J_URI = os.getenv("TEST_NEO4J_URI", "bolt://localhost:7687")
TEST_NEO4J_USER = os.getenv("TEST_NEO4J_USER", "neo4j")
TEST_NEO4J_PASSWORD = os.getenv("TEST_NEO4J_PASSWORD", "Radeon12300")

class TestNVExploreVisual(unittest.TestCase):
    def setUp(self):
        self.handler = Neo4jStorage(TEST_NEO4J_URI,
                                    TEST_NEO4J_USER,
                                    TEST_NEO4J_PASSWORD)
        self.visual = NetVisExploreVisual(self.handler)


        
    def test_expand_node(self):
        res = self.handler.get()
        view = self.visual.build(res[0].identifier)

        elements = self.visual.get_view_elements()
        new_elements = self.visual.get_visual_element(elements)
        node_data,elements = self.visual.expand_node(elements[0]["data"]["id"],
                                                     new_elements)
        style = self.visual.get_style()
        
        for e in elements:
            if "source" in e["data"]:
                self.assertEqual(e["data"]["source"],node_data.id)

        expected_selectors = [".node_colour",".edge_colour"]
        for s in style:
            for index,e in enumerate(expected_selectors):
                if e in s["selector"]:
                    expected_selectors.pop(index)
                    break

        self.assertTrue(len(expected_selectors)==0)

    def test_compress_node(self):
        res = self.handler.get()
        view = self.visual.build(res[0].identifier)
        elements = self.visual.get_view_elements()
        self.visual.get_visual_element(elements)

        final_elements = self.visual.compress_node(elements[0]["data"]["id"],
                                                   elements)
        self.assertTrue(len(final_elements) == 1)

    def test_expand_compress(self):
        # Process: expand, expand, compress leaf

        res = self.handler.get()
        view = self.visual.build(res[0].identifier)
        elements = self.visual.get_view_elements()
        elements_store = elements.copy()
        self.visual.get_visual_element(elements)
        _,elements = self.visual.expand_node(elements[0]["data"]["id"],elements)
        _,elements = self.visual.expand_node(elements[1]["data"]["id"],elements)

        for e in elements:
            if "source" in e["data"] and e["data"]["source"] == elements[1]["data"]["id"]:
                compress_node = e["data"]["target"]
                break
        final_elements = self.visual.compress_node(compress_node,elements)
        self.assertCountEqual(final_elements,elements)

        
        