import os
import sys
import unittest
from rdflib import Graph
from rdflib import RDF
sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..", ".."))
sys.path.insert(0, os.path.join("..", "..", ".."))

from app.tools.db_interface.db_interface import DatabaseInterface
from app.tools.data_transformer.data_transformer import DataTransformer

class TestDataTransformer(unittest.TestCase):
    def test_generate_identifier(self):
        db_interface = DatabaseInterface()
        transformer = DataTransformer()
        
        pe,ce = db_interface.download_all()
        replacement_map = {}
        pe = transformer.replace_identifiers(pe,replacement_map)
        ce = transformer.replace_identifiers(ce,replacement_map)
        pe = transformer.canonicalise(pe,replacement_map)
        ce = transformer.canonicalise(ce,replacement_map)
        pe = transformer.replace_references(pe,replacement_map)
        ce = transformer.replace_references(ce,replacement_map)

        


        # -- Test
        for p in pe:
            for syn in p.synonyms:
                if syn[0] in replacement_map:
                    self.assertEqual(replacement_map[syn[0]],p.id)
                    break
            else:
                self.fail()
            for r_type, rels in p.relationships.items():
                for rel in rels:
                    self.assertIn(rel,replacement_map.values())

        for c in ce:
            for syn in c.synonyms:
                if syn[0] in replacement_map:
                    self.assertEqual(replacement_map[syn[0]],c.id)
                    break
            else:
                self.fail()

            for r_type, rels in c.relationships.items():
                for rel in rels:
                    self.assertIn(rel[1],replacement_map.values())


    def test_retrieve_transformed_data(self):
        transformer = DataTransformer()
        merged = Graph()
        for g in transformer.retrieve_transformed_data(50):
            merged += g

        subjects = set(merged.subjects())
        typed_subjects = set(s for s, _, _ in 
                             merged.triples((None, RDF.type, None)))
        untyped = subjects - typed_subjects
        self.assertEqual(len(untyped), 0, f"Found untyped subjects: {untyped}")
        