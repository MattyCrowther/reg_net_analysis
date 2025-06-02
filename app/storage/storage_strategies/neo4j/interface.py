import time
import json
from typing import Optional, Dict
from graphdatascience import GraphDataScience
from graphdatascience.error.unable_to_connect import UnableToConnectError
from neo4j.exceptions import DatabaseError, ClientError

from app.storage.storage_strategies.neo4j.gds.projector import Projection
from app.storage.storage_strategies.neo4j.gds.procedures import Procedures
from app.storage.storage_strategies.neo4j.query_builder import QueryBuilder

def _connect_db(uri: str, auth: tuple) -> GraphDataScience:
    attempts = 1
    while attempts < 10:
        try:
            return GraphDataScience(uri, auth=auth)
        except UnableToConnectError:
            print(f'Attempt {attempts} failed to connect to Neo4j. Retrying...')
            time.sleep(5)
            attempts += 1
    else:
        raise UnableToConnectError("Can't connect to Neo4j database after multiple attempts.")

class Neo4jInterface:
    def __init__(self, uri: str, username: str = None, 
                 password: str = None):
        self.qry_builder = QueryBuilder()
        try:
            auth = (username,password)
            self._driver = _connect_db(uri, auth)
        except UnableToConnectError:
            self._driver = None
            raise
        self.project = Projection(self._driver)
        self.procedure = Procedures(self._driver)

    def close(self):
        if self._driver:
            self._driver.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _run_cypher(self, query: str, params: Optional[Dict] = None):
        params = params or {}
        try:
            result = self._driver.run_cypher(query, params)
            if result.empty:
                return []
            return [list(row) for _, row in result.iterrows()]
        except (DatabaseError, ClientError) as e:
            raise e
    
    def drop(self):
        qry = self.qry_builder.drop()
        return self._run_cypher(qry)
    
    def get_property(self,key):
        query = self.qry_builder.get_property(key)
        retval = self._run_cypher(query)
        return retval

    def add_node(self, label: str, identifier: str, properties: Optional[Dict] = None):
        properties = properties or {}
        properties = {k: json.dumps(v) if isinstance(v, dict) 
                      else v for k, v in properties.items()}
        query,params = self.qry_builder.merge_node_query(label, identifier, properties)
        return [r[0] for r in self._run_cypher(query, params)]
    
    def add_relationship(self, from_id: str, 
                         to_id: str, relationship_type: str, 
                         from_label: Optional[str] = None, 
                         to_label: Optional[str] = None, 
                         properties: Optional[Dict] = None):
        properties = properties or {}

        query = self.qry_builder.merge_relationship_query(from_label=from_label, 
                                                          to_label=to_label, 
                                                          rel_type=relationship_type)
        params = {'from_id': from_id, 'to_id': to_id, 'properties': properties}
        
        return [r[0] for r in self._run_cypher(query, params)]

    def update_node(self, identifier: str, 
                    type:str = None,
                    properties: Optional[Dict] = None):
        properties = properties or {}
        query = self.qry_builder.update_node_query('identifier',
                                                   type, properties)
        params = {'identifier': identifier, 'properties': properties}
        return [r[0] for r in self._run_cypher(query, params)]

    def get_node(self, label: Optional[str] = None, identifier: Optional[str] = None, 
                 get_relationships: bool = False, **kwargs):
        identifier_key = "identifier" if identifier is not None else None
        query = self.qry_builder.get_node_query(label, identifier_key, 
                                                extra_filters=kwargs, 
                                                get_relationships=get_relationships)
        params = {}
        if identifier:
            params['identifier'] = identifier
        for k, v in kwargs.items():
            params[f"filter_{k}"] = v
        results = self._run_cypher(query, params)
        return results if get_relationships else [r[0] for r in results]

    def get_nodes(
        self,
        labels: Optional[list] = None,
        identifiers: Optional[list] = None,
        get_relationships: Optional[bool] = False
    ):
        query = self.qry_builder.get_nodes_query(
            labels,
            identifiers,
            get_relationships=get_relationships
        )

        params = {}
        if labels:
            params["labels"] = list(labels)
        if identifiers:
            params["identifiers"] = list(identifiers)

        results = self._run_cypher(query, params)        
        return results
    
    def get_relationship(self, from_label: Optional[str] = None, 
                         from_id: Optional[str] = None, 
                         to_label: Optional[str] = None, 
                         to_id: Optional[str] = None, 
                         relationship_type: Optional[str] = None,
                         return_nodes: Optional[bool] = False):
        
        query = self.qry_builder.get_relationship_query(from_label, to_label, 
                                                        relationship_type,
                                                        from_id,to_id,
                                                        return_nodes=return_nodes)
        params = {}
        if from_id:
            params["from_id"] = from_id
        if to_id:
            params["to_id"] = to_id
        if not return_nodes:
            return [r[0] for r in self._run_cypher(query, params)]
        return self._run_cypher(query, params) 
    
    def get_relationships(self,node_identifier):
        query = self.qry_builder.get_relationships_query(node_identifier)
        params = {"node_identifier":node_identifier}
        return self._run_cypher(query, params)
    
    def remove(self, identifier):
        identifier_key = "identifier"
        query = self.qry_builder.remove_node_query(identifier_key)
        params = {'identifier': identifier}
        return [r[0] for r in self._run_cypher(query, params)]


    def node_count(self):
        qry = self.qry_builder.node_count()
        return self._run_cypher(qry)[0][0]
    
    def edge_count(self):
        qry = self.qry_builder.edge_count()
        return self._run_cypher(qry)[0][0]
    
    def get_isolated_nodes(self):
        qry = self.qry_builder.isolated_nodes()
        return [r[0] for r in self._run_cypher(qry)]
    
    def get_degree_distribution(self):
        qry = self.qry_builder.degree_distribution()
        return self._run_cypher(qry)
    
    def get_bidirectional(self):
        qry = self.qry_builder.bidirectional_edges()
        return self._run_cypher(qry)[0][0]
    
    def get_node_labels(self):
        qry = self.qry_builder.node_labels()
        return [item for sublist in self._run_cypher(qry) 
                for item in sublist] 
        