import build_util as bu
import warnings
warnings.filterwarnings("ignore")
from entities.abstract_entity import *
from entities.genetic import *
from entities.protein import *
from entities.chemical import *
from entities.interaction import *
from entities.synonym import *
from entities.position import *

def produce_ontology_graph():
    graph = bu.produce_ontology(__name__)
    graph.serialize("model.xml",format="pretty-xml")

if __name__ == "__main__":
    produce_ontology_graph()