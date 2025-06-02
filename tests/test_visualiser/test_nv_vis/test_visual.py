import os
import sys
import unittest

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
from app.tools.visualiser.builder.net_vis_builder import NetVisBuilder
from app.tools.visualiser.visual.visual import NetVisVisual
from app.storage.storage_strategies.neo4j.storage import Neo4jStorage

TEST_NEO4J_URI = os.getenv("TEST_NEO4J_URI", "bolt://localhost:7687")
TEST_NEO4J_USER = os.getenv("TEST_NEO4J_USER", "neo4j")
TEST_NEO4J_PASSWORD = os.getenv("TEST_NEO4J_PASSWORD", "Radeon12300")

class TestLabelHandler(unittest.TestCase):
    def setUp(self):
        self.handler = Neo4jStorage(TEST_NEO4J_URI,
                                    TEST_NEO4J_USER,
                                    TEST_NEO4J_PASSWORD)
        self.visual = NetVisVisual(self.handler)
        
    def test_expand_node(self):
        view = self.visual.set_view("FullViewBuilder")
        elements = self.visual.get_view_elements()
        new_elements = self.visual.get_visual_element(elements)
        node_data,elements = self.visual.expand_node(elements[0]["data"]["id"],
                                                     new_elements)
        style = self.visual.get_style()
        
        for e in elements:
            if "source" in e["data"]:
                self.assertEqual(e["data"]["source"],node_data.identifier)

        expected_selectors = [".node_colour_Equipment",
                              ".node_colour_Experiment",
                              ".edge_colour_HAS_EXPERIMENT"]
        for s in style:
            for e in expected_selectors:
                if s["selector"] in expected_selectors:
                    expected_selectors.pop(expected_selectors.index(s["selector"]))
                    break

        self.assertTrue(len(expected_selectors)==0)

    def test_expand_node_full(self):
        view = self.visual.set_view()
        elements = self.visual.get_view_elements()
        new_elements = self.visual.get_visual_element(elements)
        node_data,elements = self.visual.expand_node(elements[0]["data"]["id"],new_elements)
        self.assertCountEqual(new_elements,elements)

    '''
    def test_expand_node_multi(self):
        view = self.visual.set_view("FullViewBuilder")
        elements = self.visual.get_view_elements()
        new_elements = self.visual.get_visual_element(elements)
        node_data,elements = self.visual.expand_node(elements[0]["data"]["id"],new_elements)
        node_data2,elements2  = self.visual.expand_node(elements[1]["data"]["id"],elements)
        node_data2,elements2  = self.visual.expand_node(elements[4]["data"]["id"],elements)
        exit()
        style = self.visual.get_style()
        for e in elements2:
            print(e)
            if "source" in e["data"]:
                self.assertTrue(e["data"]["source"] == node_data.identifier or e["data"]["source"] == node_data2.identifier)

        expected_selectors = [".node_colour_Equipment",
                              ".node_colour_Experiment",
                              ".edge_colour_HAS_EXPERIMENT"]
        for s in style:
            for e in expected_selectors:
                if s["selector"] in expected_selectors:
                    expected_selectors.pop(expected_selectors.index(s["selector"]))
                    break

        self.assertTrue(len(expected_selectors)==0)
    '''

    def test_compress_node(self):
        view = self.visual.set_view("FullViewBuilder")
        elements = self.visual.get_view_elements()
        elements_store = elements.copy()
        self.visual.get_visual_element(elements)
        _,elements = self.visual.expand_node(elements[0]["data"]["id"],elements)
        new_elements = self.visual.compress_node(elements[0]["data"]["id"],elements)
        self.assertCountEqual(elements_store,new_elements)

        _,elements = self.visual.expand_node(elements[0]["data"]["id"],elements)

    def test_expand_compress(self):
        # Process: expand, expand, compress leaf

        view = self.visual.set_view("FullViewBuilder")
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

        
        