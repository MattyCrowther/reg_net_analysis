import os
import sys
import unittest

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..", ".."))
sys.path.insert(0, os.path.join("..", "..", ".."))

from app.storage.storage_strategies.neo4j.storage import Neo4jStorage
from app.model.model import model
TEST_NEO4J_URI = os.getenv("TEST_NEO4J_URI", "bolt://localhost:7687")
TEST_NEO4J_USER = os.getenv("TEST_NEO4J_USER", "neo4j")
TEST_NEO4J_PASSWORD = os.getenv("TEST_NEO4J_PASSWORD", "Radeon12300")

class TestGDSProject(unittest.TestCase):
    def setUp(self):
        self._handler = Neo4jStorage(TEST_NEO4J_URI,
                                       TEST_NEO4J_USER,
                                       TEST_NEO4J_PASSWORD)
        

    def test_all_graph(self):
        self._handler.project.drop("full_graph")
        res,_ = self._handler.project.full_graph()
        self.assertEqual(res.node_count(),self._handler.node_count())
        self.assertEqual(res.relationship_count(),self._handler.edge_count())


    def test_interaction_graph(self):
        nv_interaction = model.identifiers.objects.interaction
        gn = "interaction"
        int_types = model.get_all_subclasses(nv_interaction)
        edges = self._handler.get_edges(node_type=int_types)
        try:
            self._handler.project.drop(gn)
        except ValueError:
            pass
        res = self._handler.project.sub_graph(gn,edge_labels=edges)
        exp_nodes = []
        num_edges = 0
        for e in self._handler.get(int_types):
            if e not in exp_nodes:
                exp_nodes.append(e)
            for rt,rels in e.relationships.items():
                for rel in rels:
                    if rel not in exp_nodes:
                        exp_nodes.append(rel)
                    num_edges += 1
        self.assertEqual(res.node_count(),len(exp_nodes))
        self.assertEqual(res.relationship_count(),num_edges)

    