import os
import sys
import unittest

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..", ".."))
sys.path.insert(0, os.path.join("..", "..", ".."))

from storage.storage_strategies.neo4j.storage import Neo4jStorage
from utility.graph_analyser import analyse
TEST_NEO4J_URI = os.getenv("TEST_NEO4J_URI", "bolt://localhost:7687")
TEST_NEO4J_USER = os.getenv("TEST_NEO4J_USER", "neo4j")
TEST_NEO4J_PASSWORD = os.getenv("TEST_NEO4J_PASSWORD", "Radeon12300")

class TestDBInterface(unittest.TestCase):
    def setUp(self):
        self._handler = Neo4jStorage(TEST_NEO4J_URI,
                                       TEST_NEO4J_USER,
                                       TEST_NEO4J_PASSWORD)
        

    def test_analyser(self):
        analyse(self._handler)