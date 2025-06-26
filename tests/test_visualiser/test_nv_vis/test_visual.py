import os
import sys
import unittest

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
from app.tools.visualiser.builder.net_vis_view_builder import NetVisBuilder
from app.tools.visualiser.visual.net_vis_view_visual import NetVisVisual
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

    def test_colour_overwrite(self):
        self.visual.set_view()
        layout,pre_elements = self.visual.build()

        pre_stylesheet = self.visual.get_style()

        builder_value = "FullViewBuilder"
        layout,elements = self.visual.build(view_builder=builder_value)
        post_stylesheet = self.visual.get_style()

        builder_value = "InteractionBuilder"#"FullViewBuilder"
        layout,elements = self.visual.build(view_builder=builder_value)
        post_stylesheet = self.visual.get_style()

        
        