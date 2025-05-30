import os
import sys
import unittest

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..", ".."))
sys.path.insert(0, os.path.join("..", "..", ".."))

from storage.storage_strategies.neo4j.storage import Neo4jStorage
import networkx as nx

TEST_NEO4J_URI = os.getenv("TEST_NEO4J_URI", "bolt://localhost:7687")
TEST_NEO4J_USER = os.getenv("TEST_NEO4J_USER", "neo4j")
TEST_NEO4J_PASSWORD = os.getenv("TEST_NEO4J_PASSWORD", "Radeon12300")

class TestGDSProcedure(unittest.TestCase):
    def setUp(self):
        self._handler = Neo4jStorage(TEST_NEO4J_URI,
                                       TEST_NEO4J_USER,
                                       TEST_NEO4J_PASSWORD)
        

    def test_components(self):
        try:
            self._handler.project.drop("full_graph")
        except ValueError:
            pass

        res = self._handler.project.full_graph()
        components = self._handler.procedure.get_components(res.name())
        self.assertIsInstance(components, dict)
        self.assertGreater(len(components), 0)

        for component_id, nodes in components.items():
            self.assertIsInstance(component_id, int)
            self.assertIsInstance(nodes, list)
            if nodes:
                node = nodes[0]
                if hasattr(node, "id"):
                    self.assertTrue(hasattr(node, "labels"))
                    self.assertTrue(hasattr(node, "items"))
                elif isinstance(node, dict):
                    self.assertIn("identifier", node)

    def test_all_shortest_path(self):
        try:
            self._handler.project.drop("full_graph")
        except ValueError:
            pass

        res = self._handler.project.full_graph()
        sps = self._handler.procedure.all_shortest_path(res.name())

        self.assertIsInstance(sps, list)
        self.assertGreater(len(sps), 0)

        for record in sps:
            self.assertIsInstance(record, tuple)
            self.assertEqual(len(record), 3)
            source, distance, target = record
            self.assertIsInstance(source, float)
            self.assertIsInstance(target, float)
            self.assertIsInstance(distance, (int, float))
            self.assertGreaterEqual(distance, 0)

    def test_density(self):
        try:
            self._handler.project.drop("full_graph")
        except ValueError:
            pass

        res = self._handler.project.full_graph()
        density = self._handler.procedure.density(res.name())

        self.assertIsInstance(density, float, "Density should be a float")
        self.assertGreaterEqual(density, 0.0, "Density should be ≥ 0")
        self.assertLessEqual(density, 1.0, "Density should be ≤ 1")

    def test_average_lcc(self):
        try:
            self._handler.project.drop("full_graph_undirected")
        except ValueError:
            pass

        res = self._handler.project.full_graph(directed=False)
        average_lcc = self._handler.procedure.average_local_clustering_coefficient(res.name())
        self.assertIsInstance(average_lcc,float)

    def test_gcc(self):
        try:
            self._handler.project.drop("full_graph_undirected")
        except ValueError:
            pass

        res = self._handler.project.full_graph(directed=False)
        gcc = self._handler.procedure.global_clustering_coefficient(res.name())
        self.assertIsInstance(gcc,float)

    def test_triangles(self):
        try:
            self._handler.project.drop("full_graph_undirected")
        except ValueError:
            pass

        res = self._handler.project.full_graph(directed=False)
        gcc = self._handler.procedure.triangles(res.name())
        self.assertIsInstance(gcc,list)
    
    def test_degree_assortativity(self):
        try:
            self._handler.project.drop("full_graph")
        except ValueError:
            pass

        res = self._handler.project.full_graph()
        gcc = self._handler.procedure.degree_assortativity(res.name())
        self.assertIsInstance(gcc,float)


    def test_degree_centrality(self):
        try:
            self._handler.project.drop("full_graph")
        except ValueError:
            pass

        res = self._handler.project.full_graph()
        gcc = self._handler.procedure.degree_centrality(res.name())
        self.assertIsInstance(gcc,list)

    def test_betweenness_centrality(self):
        try:
            self._handler.project.drop("full_graph")
        except ValueError:
            pass

        res = self._handler.project.full_graph()
        gcc = self._handler.procedure.betweenness_centrality(res.name())
        self.assertIsInstance(gcc,list)

    def test_closeness_centrality(self):
        try:
            self._handler.project.drop("full_graph")
        except ValueError:
            pass

        res = self._handler.project.full_graph()
        gcc = self._handler.procedure.closeness_centrality(res.name())
        self.assertIsInstance(gcc,list)

    def test_page_rank(self):
        try:
            self._handler.project.drop("full_graph")
        except ValueError:
            pass

        res = self._handler.project.full_graph()
        gcc = self._handler.procedure.page_rank(res.name())
        self.assertIsInstance(gcc,list)

    def test_eigenvector_centrality(self):
        try:
            self._handler.project.drop("full_graph")
        except ValueError:
            pass

        res = self._handler.project.full_graph()
        gcc = self._handler.procedure.eigenvector_centrality(res.name())
        self.assertIsInstance(gcc,list)

    def test_node_similarity(self):
        try:
            self._handler.project.drop("full_graph")
        except ValueError:
            pass

        res = self._handler.project.full_graph()
        gcc = self._handler.procedure.node_similarity(res.name())
        self.assertIsInstance(gcc,list)

    def test_bfs(self):        
        source = self._handler.get()[0]
        res = self._handler.project.full_graph(directed=False)
        gcc = self._handler.procedure.bfs(res.name(),source,max_depth=5)
        self.assertIsInstance(gcc,nx.DiGraph)