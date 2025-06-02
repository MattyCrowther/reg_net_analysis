import os
import sys
import unittest

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..", ".."))
sys.path.insert(0, os.path.join("..", "..", ".."))

from app.tools.db_interface.db_interface import DatabaseInterface

class TestDBInterface(unittest.TestCase):
    def test_db_interface(self):
        interface = DatabaseInterface()
        pe,ce = interface.download_all(True)
        pe1,ce1 = interface.download_all(False)
        for r in pe:
            self.assertIn(r,pe1)
        for r in ce:
            self.assertIn(r,ce1)

