import os
import sys
import unittest

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
from app.tools.visualiser.builder.net_vis_builder import NetVisBuilder
from app.tools.visualiser.visual.visual import NetVisVisual
from app.storage.storage_strategies.neo4j.storage import Neo4jStorage
from app.model.model import model

TEST_NEO4J_URI = os.getenv("TEST_NEO4J_URI", "bolt://localhost:7687")
TEST_NEO4J_USER = os.getenv("TEST_NEO4J_USER", "neo4j")
TEST_NEO4J_PASSWORD = os.getenv("TEST_NEO4J_PASSWORD", "Radeon12300")

nv_has_part = str(model.identifiers.predicates.has_part)
class TestNVBuilder(unittest.TestCase):
    def setUp(self):
        self.handler = Neo4jStorage(TEST_NEO4J_URI,
                                    TEST_NEO4J_USER,
                                    TEST_NEO4J_PASSWORD)
        self.builder = NetVisBuilder(self.handler)
        
    def test_expand_node(self):
        view = self.builder.set_view("FullViewBuilder")
        elements = self.builder.get_view_elements()

        ret_val = self.builder.expand_node(elements[0]["data"]["id"])
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


    def test_interaction_view(self):
        view = self.builder.set_view("InteractionBuilder")
        elements = self.builder.get_view_elements()

    def test_structural_view(self):
        self.builder.set_view("StructuralViewBuilder")
        elements = self.builder.get_view_elements()
        view = self.builder.view
        expected_edges = self.handler.get_edges(edge_type=nv_has_part)
        expected_nodes = [node for n, v, _ in expected_edges 
                          for node in (n.identifier, v.identifier)]
        actual_nodes = []
        actual_edges = []
        for element in elements:
            if "source" in element["data"]:
                actual_edges.append((element["data"]["source"],
                                     element["data"]["target"]))               
                for n,v,e in expected_edges:
                    if (n.identifier == element["data"]["source"] and 
                        v.identifier == element["data"]["target"]):
                        break
                else:
                    self.fail()
            else:
                actual_nodes.append(element["data"]["id"])
                node = view.get_element(element["data"]["id"])
                for rt,rels in node.relationships.items():
                    self.assertEqual(rt,nv_has_part)
                    for r in rels:
                        self.assertIn(r,expected_nodes)

        self.assertEqual(len(expected_edges),len(actual_edges))
        self.assertEqual(len(expected_nodes),len(actual_nodes))

        for a_node in actual_nodes:
            self.assertIn(a_node,expected_nodes)
        expected_edge_ids = [(n.identifier,v.identifier) 
                             for n,v,_ in expected_edges]
        for a_edge in actual_edges:
            self.assertIn(a_edge,expected_edge_ids)