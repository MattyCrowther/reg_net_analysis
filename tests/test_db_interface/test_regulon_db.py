import os
import sys
import unittest

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..", ".."))
sys.path.insert(0, os.path.join("..", "..", ".."))

from db_interface.databases.regulondb import RegulonDB
from db_interface.databases.abstract_database import PhysicalEntity,ConceptualEntity
class TestRegulonDB(unittest.TestCase):
    def setUp(self):
        """Set up a live client before each test."""
        self.client = RegulonDB()
        self.data = self.client.fetch_all()

    def test_fetch_all(self):
        """Test fetching all regulated genes."""
        pe = []
        ce = []
        for item in self.data:
            if isinstance(item,PhysicalEntity):
                pe.append(item)
            elif isinstance(item,ConceptualEntity):
                ce.append(item)
            else:
                self.fail()

        seen_ids = []
        for e in pe:
            if e.id in seen_ids:
                self.fail()
            seen_ids.append(e.id)


    def test_entity_types_are_correct(self):
        """Ensure all returned entities are either PhysicalEntity or ConceptualEntity."""
        for item in self.data:
            self.assertTrue(
                isinstance(item, (PhysicalEntity, ConceptualEntity)),
                f"Unexpected entity type: {type(item)}"
            )

    def test_unique_entity_ids(self):
        """Ensure no duplicate entity IDs exist."""
        seen_ids = set()
        for item in self.data:
            self.assertNotIn(item.id, seen_ids, f"Duplicate ID found: {item.id}")
            seen_ids.add(item.id)

    def test_basic_distribution_by_class(self):
        """Optional: log how many of each entity type we got (manual debug aid)."""
        pe_count = sum(isinstance(e, PhysicalEntity) for e in self.data)
        ce_count = sum(isinstance(e, ConceptualEntity) for e in self.data)
        print(f"Total entities: {len(self.data)}")
        print(f"  PhysicalEntity: {pe_count}")
        print(f"  ConceptualEntity: {ce_count}")
        self.assertGreater(pe_count, 0, "Expected some PhysicalEntities")
        self.assertGreater(ce_count, 0, "Expected some ConceptualEntities")


    def test_conceptual_entities_participants_exist_as_physical_entities(self):
        """Ensure every participant in ConceptualEntity exists as a PhysicalEntity."""
        # Index all physical entity IDs for quick lookup
        pe_ids = {e.id for e in self.data if isinstance(e, PhysicalEntity)}

        # Now check each CE
        for ce in [e for e in self.data if isinstance(e, ConceptualEntity)]:
            for role, participant_id in ce._relationships.get("participants", []):
                self.assertIn(
                    participant_id,
                    pe_ids,
                    msg=f"Participant ID {participant_id} in {ce.id} not found among PhysicalEntities"
                )


    def test_physical_entity_json_round_trip(self):
        """Test that PhysicalEntity can serialize and deserialize correctly."""
        original_entities = [e for e in self.data if isinstance(e, PhysicalEntity)]

        for entity in original_entities:
            json_data = entity.to_json()
            restored = PhysicalEntity.from_json(json_data)

            self.assertEqual(restored.id, entity.id)
            self.assertEqual(restored.name, entity.name)
            self.assertEqual(restored.sequence, entity.sequence)
            self.assertEqual(restored.confidence, entity.confidence)
            self.assertEqual(restored.synonyms, entity.synonyms)
            self.assertEqual(
                restored._relationships.get("contains", []),
                entity._relationships.get("contains", []),
                f"Mismatch in 'contains' for {entity.id}"
            )