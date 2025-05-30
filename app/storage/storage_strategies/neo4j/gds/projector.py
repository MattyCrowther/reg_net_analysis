from graphdatascience import GraphDataScience

from app.storage.storage_strategies.neo4j.gds.query_builder import GDSQueryBuilder

class Projection():
    def __init__(self, driver: GraphDataScience):
        self._driver = driver
        self._qry_builder = GDSQueryBuilder()
    
    def project(self, name, nodes, edges, **kwargs):
        return self._driver.graph.project(name, nodes, 
                                          edges,**kwargs)
        
    def drop(self, name):
        g = self.get_graph(name)
        g.drop()

    def names(self):
        res = self._driver.graph.list()
        return (list(res["graphName"]))
        
    def get_graph(self, graph_name):
        return self._driver.graph.get(graph_name)

    def cypher_project(self,name,node_labels=None,edge_labels=None,
                       node_properties=None):
        qry = self._qry_builder.cypher_project(name, node_labels,
                                                edge_labels,node_properties)
        ret = self._run(qry)
        return self.get_graph(name)
        
    def sub_graph(self, o_name, n_name, nodes, edges):
        qry = self._qry_builder.subgraph(o_name, n_name, nodes, edges)
        ret = self._run(qry)
        return self.get_graph(n_name)
        
    def mutate(self, name, types, mutate_type, node_labels=None):
        if node_labels and not isinstance(node_labels, list):
            node_labels = [str(node_labels)]
        qry = self._qry_builder.mutate(name, types, mutate_type, node_labels)
        return self._run(qry)
        
    def _run(self,qry):
        return self._driver.run_cypher(qry)