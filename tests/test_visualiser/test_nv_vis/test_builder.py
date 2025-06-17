import os
import sys
import unittest

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
from app.tools.visualiser.builder.net_vis_builder import NetVisBuilder
from app.storage.storage_strategies.neo4j.storage import Neo4jStorage
from app.model.model import model

TEST_NEO4J_URI = os.getenv("TEST_NEO4J_URI", "bolt://localhost:7687")
TEST_NEO4J_USER = os.getenv("TEST_NEO4J_USER", "neo4j")
TEST_NEO4J_PASSWORD = os.getenv("TEST_NEO4J_PASSWORD", "Radeon12300")

nv_has_part = str(model.identifiers.predicates.has_part)
nv_interaction = model.identifiers.objects.interaction
nv_physical_entity = model.identifiers.objects.physical_entity

class TestNVBuilder(unittest.TestCase):
    def setUp(self):
        self.handler = Neo4jStorage(TEST_NEO4J_URI,
                                    TEST_NEO4J_USER,
                                    TEST_NEO4J_PASSWORD)
        self.builder = NetVisBuilder(self.handler)
        
    def test_verbose_interaction_view(self):
        self.builder.set_view("VerboseInteractionBuilder")
        elements = self.builder.get_view_elements()
        view = self.builder.view

        i_classes = [str(n) for n in 
                     model.get_all_subclasses(nv_interaction)]
        c_classes = [str(n) for n in 
                     model.get_all_subclasses(nv_physical_entity)]
        for element in elements:
            if "source" in element["data"]:
                source = element["data"]["source"]
                target = element["data"]["target"]
                source_obj = view.get_node(source)
                target_obj = view.get_node(target)
                edge = view.get_edge_type(source,target)
                direction = model.get_interaction_direction(edge)
                if direction == model.identifiers.objects.input:
                    self.assertIn(target_obj.type,i_classes)
                    self.assertIn(source_obj.type,c_classes)
                elif direction == model.identifiers.objects.output:
                    self.assertIn(source_obj.type,i_classes)
                    self.assertIn(target_obj.type,c_classes)
                else:
                    self.fail(direction)

    def test_interaction_view(self):
        self.builder.set_view("InteractionBuilder")
        elements = self.builder.get_view_elements()
        view = self.builder.view

        c_classes = [str(n) for n in 
                     model.get_all_subclasses(nv_physical_entity)]
        for element in elements:
            if "source" in element["data"]:
                source = element["data"]["source"]
                target = element["data"]["target"]
                source_obj = view.get_node(source)
                target_obj = view.get_node(target)
                self.assertIn(target_obj.type,c_classes)
                self.assertIn(source_obj.type,c_classes)


    def test_structural_view(self):
        self.builder.set_view("StructuralViewBuilder")
        elements = self.builder.get_view_elements()
        view = self.builder.view
        expected_edges = self.handler.get_edges(edge_type=nv_has_part)
        expected_nodes = list(set([node for n, v, _ in expected_edges 
                          for node in (n.identifier, v.identifier)]))
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
                    self.fail(element)
            else:
                if element["data"]["id"] not in actual_nodes:
                    actual_nodes.append(element["data"]["id"])
                node = view.get_node(element["data"]["id"])
                for edge in view.edges(node):
                    self.assertEqual(edge.type,nv_has_part)
                    self.assertIn(edge.v.id,expected_nodes)

        self.assertEqual(len(expected_edges),len(actual_edges))
        self.assertEqual(len(expected_nodes),len(actual_nodes))
        
        for a_node in actual_nodes:
            self.assertIn(a_node,expected_nodes)
        expected_edge_ids = [(n.identifier,v.identifier) 
                             for n,v,_ in expected_edges]
        for a_edge in actual_edges:
            self.assertIn(a_edge,expected_edge_ids)