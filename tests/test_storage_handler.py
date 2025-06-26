import os
import sys
import unittest

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..", ".."))
sys.path.insert(0, os.path.join("..", "..", ".."))

from app.tools.db_interface.db_interface import DatabaseInterface
from app.storage.storage_handler import StorageHandler
from app.storage.storage_strategies.storage_objects import StorageObject
from app.tools.data_transformer.data_transformer import DataTransformer

TEST_NEO4J_URI = os.getenv("TEST_NEO4J_URI", "bolt://localhost:7687")
TEST_NEO4J_USER = os.getenv("TEST_NEO4J_USER", "neo4j")
TEST_NEO4J_PASSWORD = os.getenv("TEST_NEO4J_PASSWORD", "Radeon12300")

class TestStorageInterface(unittest.TestCase):
    def test_db_interface(self):
        db_interface = DatabaseInterface()
        interface = StorageHandler("neo4j",TEST_NEO4J_URI,
                                   TEST_NEO4J_USER,
                                   TEST_NEO4J_PASSWORD)
        transformer = DataTransformer()
        #pe,ce = db_interface.download_all(False)
        #replacement_map = {}
        #pe = transformer.replace_identifiers(pe,replacement_map)
        #ce = transformer.replace_identifiers(ce,replacement_map)
        #pe = transformer.replace_references(pe,replacement_map)
        #ce = transformer.replace_references(ce,replacement_map)

        #entities = transformer.canonicalise(pe + ce)
        
        num_elements = None
        # GOAL: Get retrived transformed data to retrive a COMPLETE subset if given.
        graphs = transformer.retrieve_transformed_data(num_elements)
        for graph in graphs:
            interface.add_rdf_graph(graph)

        count = len(interface.get())
        self.assertEqual(len(graphs),count)
        


    def test_export_load(self):
        interface = StorageHandler("neo4j",TEST_NEO4J_URI,
                                   TEST_NEO4J_USER,
                                   TEST_NEO4J_PASSWORD)
        
        out_fn = "temp.json"
        pre_data = interface.get()

        interface.export(out_fn)
        interface.load(out_fn)

        post_data = interface.get()

        os.remove(out_fn)
        self.assertCountEqual(pre_data,post_data)

    def test_get_in_relationships(self):
        interface = StorageHandler("neo4j",TEST_NEO4J_URI,
                                   TEST_NEO4J_USER,
                                   TEST_NEO4J_PASSWORD)
        
        res = interface.get()
        node = res[0]

        results = interface.get_in_relationships(node.identifier)
        for n,e in results:
            self.assertIsInstance(n,StorageObject)
            self.assertIsInstance(e,str)
