from typing import Optional,Dict

from urllib.parse import urlparse

class QueryBuilder:
    def drop(self):
        return """MATCH(n) DETACH DELETE n"""
    
    def merge_node_query(
        self, label: str, identifier, properties: Optional[dict] = None
    ) -> str:
        """
        Returns a query that MERGEs a node with optional properties.
        """
        properties = properties or {}
        if is_url(label):
            label = f"`{label}`"
        graph_props = {}
        for k,v in properties.items():
            if is_url(k):
                k = k
            graph_props[k] = v
            
        params = {'identifier': identifier, 'properties': graph_props}
        return (
            f"MERGE (n:{label} {{ identifier: $identifier }})\n"
            f"ON CREATE SET n += $properties\n"
            f"ON MATCH SET n += $properties\n"
            f"RETURN n"
        ),params

    def merge_relationship_query(
        self,
        from_label: Optional[str],
        to_label: Optional[str],
        rel_type: str,
        from_id_key: str = "identifier",
        to_id_key: str = "identifier",
    ) -> str:
        """
        Returns a query that MERGEs a relationship with optional labels.
        If labels are None, it will create or match any node with the given ID.
        """

        from_merge = f"(a:{from_label} {{ {from_id_key}: $from_id }})" if from_label else f"(a {{ {from_id_key}: $from_id }})"
        to_merge = f"(b:{to_label} {{ {to_id_key}: $to_id }})" if to_label else f"(b {{ {to_id_key}: $to_id }})"
        if is_url(rel_type):
            rel_type = f"`{rel_type}`"
        return (
            f"MERGE {from_merge}\n"
            f"MERGE {to_merge}\n"
            f"MERGE (a)-[r:{rel_type}]->(b)\n"
            f"RETURN r"
        )

    def update_node_query(self, identifier_key: str, type: str = None, properties: Optional[dict] = None) -> str:
        """
        Matches a node by identifier (ignoring labels), applies a new label,
        and updates properties. Appends to lists and overwrites scalars.
        """
        properties = properties or {}

        query = f"MATCH (n {{ {identifier_key}: $identifier }})\n"

        if type:
            if is_url(type):
                type = f"`{type}`"
            query += f"SET n:{type}\n"

        set_clauses = []
        for key, value in properties.items():
            if is_url(key):
                key = f"`{key}`"
            if isinstance(value, list):
                clause = (
                    f"n.{key} = CASE WHEN n.{key} IS NULL THEN $properties.{key} "
                    f"ELSE n.{key} + $properties.{key} END"
                )
            else:
                clause = f"n.{key} = $properties.{key}"
            set_clauses.append(clause)

        if set_clauses:
            query += "SET " + ",\n    ".join(set_clauses) + "\n"

        query += "RETURN n"
        return query

    def get_node_query(
        self,
        label: Optional[str] = None,
        identifier_key: Optional[str] = None,
        extra_filters: Optional[Dict[str, any]] = None,
        get_relationships: bool = False,
        rhs_identifier_key: str = "identifier"
    ) -> str:
        """
        Returns a query to get nodes with optional label, identifier, and filters.
        Optionally retrieves the relationship labels and the connected node's identifier 
        when `get_relationships=True`.
        """
        cypher = ["MATCH (n)"]
        conditions = []

        if label:
            cypher[0] = f"MATCH (n:{label})"
        if identifier_key:
            conditions.append(f"n.{identifier_key} = $identifier")

        if extra_filters:
            for k in extra_filters:
                param_name = f"filter_{k}"
                conditions.append(f"n.{k} = ${param_name}")

        if conditions:
            cypher.append("WHERE " + " AND ".join(conditions))

        if get_relationships:
            cypher.append(f"""
            OPTIONAL MATCH (n)-[r]->(m)
            RETURN n, COLLECT(DISTINCT {{r: TYPE(r), v: m.{rhs_identifier_key}}}) AS relationships
            """)
        else:
            cypher.append("RETURN n")

        return "\n".join(cypher)

    def get_nodes_query(
        self,
        labels: Optional[list[str]] = None,
        identifiers: Optional[list[str]] = None,
        extra_filters: Optional[Dict[str, any]] = None,
        get_relationships: bool = False,
        rhs_identifier_key: str = "identifier"
    ) -> str:
        """
        Returns a Cypher query to retrieve nodes that have any of the specified labels,
        with optional property filters. When `get_relationships=True`, also returns
        outgoing relationship types and connected node identifiers.
        """
        cypher = ["MATCH (n)"]
        conditions = []

        if labels:
            conditions.append("ANY(lbl IN labels(n) WHERE lbl IN $labels)")

        if identifiers:
            conditions.append("n.identifier IN $identifiers")

        if extra_filters:
            for k in extra_filters:
                conditions.append(f"n.{k} = $filter_{k}")

        if conditions:
            cypher.append("WHERE " + " AND ".join(conditions))

        if get_relationships:
            cypher.append(
                f"OPTIONAL MATCH (n)-[r]->(m) "
                f"RETURN n, COLLECT(DISTINCT {{r: TYPE(r), v: m.{rhs_identifier_key}}}) AS relationships"
            )
        else:
            cypher.append("RETURN n")

        return " ".join(cypher)

    
    def get_relationship_query(
        self,
        from_label: Optional[str] = None,
        to_label: Optional[str] = None,
        rel_type: Optional[str] = None,
        from_id: Optional[str] = None,
        to_id: Optional[str] = None,
        return_nodes: Optional[bool] = False
    ) -> str:
        """
        Returns a query to get relationships with optional node labels, identifiers, and relationship type.
        If return_nodes is True, also returns the connected nodes (a and b).
        """
        match_clause = "MATCH (a)-[r]->(b)"
        conditions = []

        if from_label:
            conditions.append(f"labels(a) = ['{from_label}']")
        if to_label:
            conditions.append(f"labels(b) = ['{to_label}']")
        if rel_type:
            conditions.append(f"type(r) = '{rel_type}'")
        if from_id:
            conditions.append(f"a.identifier = '{from_id}'")
        if to_id:
            conditions.append(f"b.identifier = '{to_id}'")

        where_clause = " AND ".join(conditions)
        query = f"{match_clause}\n"
        if where_clause:
            query += f"WHERE {where_clause}\n"

        if return_nodes:
            query += "RETURN a, r, b"
        else:
            query += "RETURN r"

        return query

    def get_relationships_query(self, node_identifier=None, node_labels=None):
        match_clause = "MATCH (a)-[r]-(b)"
        conditions = []

        # Node identifier condition
        if node_identifier:
            conditions.append(f"a.identifier = '{node_identifier}'")

        # Label conditions (match any)
        if node_labels:
            label_conditions = [f"'{label}' IN labels(a)" for label in node_labels]
            conditions.append("(" + " OR ".join(label_conditions) + ")")

        where_clause = " AND ".join(conditions)
        
        query = f"{match_clause}\n"
        if where_clause:
            query += f"WHERE {where_clause}\n"
        query += "RETURN a, r, b"

        return query
    
    def get_in_relationships_query(self, node_identifier):
        # Only match relationships where 'a' is the target (incoming)
        match_clause = "MATCH (a)<-[r]-(b)"
        conditions = [f"a.identifier = '{node_identifier}'"]

        where_clause = " AND ".join(conditions)
        query = f"{match_clause}\n"
        if where_clause:
            query += f"WHERE {where_clause}\n"
        query += "RETURN a, r, b"
        return query

    def remove_node_query(self,identifier_key):
        return f"MATCH (n {{ {identifier_key}: $identifier }}) DETACH delete n" 
    
    def get_property(self, property_key: str, label: Optional[str] = None) -> str:
        if label:
            return (
                f"MATCH (n:{label})\n"
                f"RETURN DISTINCT n.{property_key} AS value"
            )
        else:
            return (
                f"MATCH (n)\n"
                f"RETURN DISTINCT n.{property_key} AS value"
            )
        
    def node_count(self):
        return """MATCH (n) RETURN count(n) AS total_nodes;"""
    
    def edge_count(self):
        return """MATCH ()-[r]->() RETURN count(r) AS total_relationships;"""

    def isolated_nodes(self):
        return """MATCH (n)
                WHERE NOT (n)--()
                RETURN n"""
    
    def degree_distribution(self):
        return """MATCH (n)
                    WITH COUNT { (n)--() } AS degree
                    RETURN degree, COUNT(*) AS frequency
                    ORDER BY degree
                """
    
    def bidirectional_edges(self):
        return """
        MATCH (a)-[r]->(b)
        WHERE (b)-[]->(a) AND id(a) < id(b)
        RETURN count(*) AS bidirectional_pairs
        """
    
    def node_labels(self):
        return """CALL db.labels() YIELD label RETURN label"""
    
    def export(self):
        return f'''
        MATCH (n1)
        OPTIONAL MATCH (n1)-[e]->()
        WITH collect(DISTINCT n1) AS a, collect(DISTINCT e) AS b
        CALL apoc.export.json.data(a, b, null, {{stream: true}})
        YIELD data
        RETURN data
        '''
    
    def id_map(self):
        return f'''
        MATCH (n)
        RETURN id(n) AS nodeId, n.identifier AS identifier
        '''

    def relationship_type(self, node_types):
        labels_str = "[" + ", ".join(f"'{label}'" for label in node_types) + "]"
        query = f"""
        WITH {labels_str} AS targetLabels
        MATCH (a)-[r]->(b)
        WHERE any(label IN labels(a) WHERE label IN targetLabels)
        OR any(label IN labels(b) WHERE label IN targetLabels)
        RETURN DISTINCT type(r) AS relationshipType
        """
        return query
    
def is_url(string):
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False