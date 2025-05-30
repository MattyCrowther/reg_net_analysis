import os
import sys
import unittest

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..", ".."))
sys.path.insert(0, os.path.join("..", "..", ".."))

from app.tools.db_interface.db_interface import DatabaseInterface
from app.tools.data_transformer.data_transformer import DataTransformer

class TestDBInterface(unittest.TestCase):
    def test_generate_identifier(self):
        db_interface = DatabaseInterface()
        transformer = DataTransformer()
        
        pe,ce = db_interface.download_all()
        replacement_map = {}
        # -- Replace IDS --
        for p in pe:
            old_id = p.id
            p = transformer.generate_identifier(p)
            replacement_map[old_id] = p.id
        for c in ce:
            old_id = c.id
            c = transformer.generate_identifier(c)
            replacement_map[old_id] = c.id
        
        # -- Replace Reference --
        for p in pe:
            for r_type, rels in p.relationships.items():
                for i, rel in enumerate(rels):
                    if rel in replacement_map:
                        rels[i] = replacement_map[rel]

        for c in ce:
            for r_type, rels in c.relationships.items():
                for i, rel in enumerate(rels):
                    type,rel = rel
                    if rel in replacement_map:
                        rels[i] = [type,replacement_map[rel]]

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

    def test_generate_identifier(self):
        db_interface = DatabaseInterface()
        transformer = DataTransformer()
        
        pe,ce = db_interface.download_all()
        replacement_map = {}
        pe = transformer.replace_identifiers(pe,replacement_map)
        ce = transformer.replace_identifiers(ce,replacement_map)
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

    def test_transform(self):
        db_interface = DatabaseInterface()
        transformer = DataTransformer()
        
        pe,ce = db_interface.download_all()
        replacement_map = {}
        pe = transformer.replace_identifiers(pe,replacement_map)
        ce = transformer.replace_identifiers(ce,replacement_map)
        pe = transformer.replace_references(pe,replacement_map)
        ce = transformer.replace_references(ce,replacement_map)
        for d in ce:
            transformer.transform(d)


    def test_transform_all(self):
        db_interface = DatabaseInterface()
        transformer = DataTransformer()
        
        pe,ce = db_interface.download_all()
        replacement_map = {}
        pe = transformer.replace_identifiers(pe,replacement_map)
        ce = transformer.replace_identifiers(ce,replacement_map)
        pe = transformer.replace_references(pe,replacement_map)
        ce = transformer.replace_references(ce,replacement_map)
        
        transformer.transform_data(ce+pe)


    def test_retrieve_transformed_data(self):
        transformer = DataTransformer()
        graphs = transformer.retrieve_transformed_data()
        print(len(graphs))
        # AQUIIIIIIIIIIIIIIIIIIIIIIIIIIIII SHIT NEEDS TO BE BETTER CHECK FOR DUPS ETC