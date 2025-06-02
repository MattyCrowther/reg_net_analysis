import networkx as nx
from app.tools.visualiser.view.view import View

class AbstractViewBuilder():
    def __init__(self,storage):
        self._storage = storage

    def _new_view(self, entities):
        return View(entities)