import uuid
import os
from pathlib import Path

from rdflib import URIRef
from rdflib import Literal
from rdflib import Graph

from app.tools.db_interface.databases.abstract_database import PhysicalEntity
from app.tools.db_interface.databases.abstract_database import ConceptualEntity
from app.tools.utility.rdf_graph_wrapper import RDFGraphWrapper
from app.model.model import model

rdf_type = model.identifiers.predicates.rdf_type
role_predicate = model.identifiers.predicates.role
name_predicate = model.identifiers.external.title
synonym_predicate = model.identifiers.external.synonym
confidence_predicate = model.identifiers.external.confidence
sequence_predicate = model.identifiers.predicates.has_sequence
has_part_predicate = model.identifiers.predicates.has_part

curr_dir = os.path.dirname(os.path.realpath(__file__))
storage_dir = os.path.join(curr_dir,"transformed_data")
if not os.path.isdir(storage_dir):
    os.mkdir(storage_dir)

class DataTransformer():
    def __init__(self):
        pass

    def generate_identifier(self,record):
        new_id = f'{model.identifiers.namespaces.nv}{uuid.uuid4()}'
        record.add_synonym(record.id)
        record.replace_id(new_id)
        return record

    def replace_identifiers(self,records,replacement_map = None):
        # -- First pass: Generate new IDs and build the replacement map --
        if replacement_map is None:
            replacement_map = {}

        for record in records:
            old_id = record.id
            record = self.generate_identifier(record)
            replacement_map[old_id] = record.id
        return records

    def replace_references(self,records,replacement_map):
        # -- Second pass: Update references using the replacement map --
        for record in records:
            for r_type, rels in record.relationships.items():
                for i, rel in enumerate(rels):
                    # Check for tuple (type, id) structure
                    if isinstance(rel, (list, tuple)) and len(rel) == 2:
                        rel_type, rel_id = rel
                        if rel_id in replacement_map:
                            rels[i] = [rel_type, replacement_map[rel_id]]
                    else:
                        # Assume it's a raw ID string
                        if rel in replacement_map:
                            rels[i] = replacement_map[rel]
        return records

    def canonicalise(self,records,replacement_map):
        # Its not as easy as i thought. For example, even if stuff does have say the same sequence, it could be the case that they are in different regions...............
        # Needs mas thought. However, intra dataset canonicalisation should happen as source where you have more control over the data....
        # Also, need to think about context vs source idependant.
        return records
        # Replacement map (old:new)
        for record in records:
            if isinstance(record,PhysicalEntity):
                res = self._find_pe_canonical(record,records)
            elif isinstance(record,ConceptualEntity):
                pass
            else:
                raise ValueError(type(record))

        
    def _find_pe_canonical(self,record,records):
        record_sequence = record.sequence
        for o_record in records:
            if not isinstance(o_record,PhysicalEntity):
                continue
            if o_record == record:
                continue
            if record_sequence is not None:
                if record_sequence != o_record.sequence:
                    continue
            
    def transform_data(self,records):
        graphs = []
        for record in records:
            graph = self.transform(record)
            fn = os.path.join(storage_dir,f'{record.id.split("/")[-1]}.ttl')
            graph.serialize(fn,"ttl")
            graphs.append(graph)
        return graphs
    
    def transform(self, record):
        graph = Graph()
        class_type = model.get_class(record.type)
        identifier = URIRef(record.id)
        graph.add((identifier,rdf_type,class_type))
        graph.add((identifier,name_predicate,Literal(record.name)))
        if record.confidence is not None:
            graph.add((identifier,confidence_predicate,Literal(record.confidence)))
        for synonym in record.synonyms:
            # Synonyms 
            graph.add((identifier,synonym_predicate,Literal(synonym[0])))
        if isinstance(record,PhysicalEntity):
            if record.sequence is not None:
                graph.add((identifier,sequence_predicate,Literal(record.sequence)))
            for role in record.roles:
                graph.add((identifier,role_predicate,Literal(role)))
            for sub_entity in record.sub_regions:
                # Currently, dont decide type of sub region 
                # or any extra information. Deicde if we wanna take more.
                # TBH, based on subject and object type, this could be infered.
                graph.add((identifier,has_part_predicate,URIRef(sub_entity)))
            # metadata??
        elif isinstance(record,ConceptualEntity):
            for p_type,p_value in record.participants:
                p_type = model.get_predicate(class_type,p_type)
                graph.add((identifier,p_type,URIRef(p_value)))
        else:
            raise ValueError(type(record))
        return RDFGraphWrapper(graph)
    

    def retrieve_transformed_data(self, max=None):
        graphs = {}
        visited = set()

        ttl_files = [f for f in os.listdir(storage_dir) if f.endswith(".ttl")]
        num_files = len(ttl_files)

        def _load_graph(fn):
            canonical_name = os.path.basename(fn)
            print(f'Seen {len(visited)}/{num_files} records ({(len(visited)/num_files) * 100:.2f}% )')
            if canonical_name in visited:
                return
            visited.add(canonical_name)

            path = os.path.join(storage_dir, fn)
            if not os.path.isfile(path):
                return

            g = Graph()
            g.parse(path)
            g = RDFGraphWrapper(g)
            graphs[canonical_name] = g

            if max is not None:
                for s, p, o in g.search((None, None, None)):
                    if isinstance(o, URIRef):
                        linked_fn = self._find_file(self._get_name(o) + ".ttl")
                        if linked_fn:
                            _load_graph(linked_fn.name)

            if max is not None and len(graphs) >= max:
                return

        for file in ttl_files:
            if file not in visited:
                _load_graph(file)
            if max is not None and len(graphs) >= max:
                break

        return list(graphs.values())





    def _get_name(self,obj):
        return obj.split("/")[-1]
    
    def _find_file(self,filename):
        path = Path(storage_dir)
        for file in path.rglob(filename):
            return file
        return None