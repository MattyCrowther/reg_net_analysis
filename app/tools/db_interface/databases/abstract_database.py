from abc import ABC, abstractmethod
from enum import Enum

class AbstractDatabase(ABC):
    @abstractmethod
    def fetch_all(self):
        """Fetch all relevant entities (e.g., genes, interactions, pathways)."""
        pass

    @abstractmethod
    def fetch_entity(self, entity_id):
        """Fetch a single entity by ID or name."""
        pass



class AbstractObject:
    def __init__(self,identifier,type,name=None):
        self._identifier = identifier
        if isinstance(type,TYPES):
            type = type.value
            
        self._type = type
        self._name = name
        self._synonyms = []
        self._relationships = {}
        self._metadata = {}
        self._confidence = None

    def __str__(self):
        return self._identifier
    
    def __eq__(self, value):
        if not isinstance(value,self.__class__):
            return False
        return self._identifier == value._identifier
    
    def merge(self,other):
        if not isinstance(other, AbstractObject) or self.id != other.id:
            raise ValueError("Can only merge with the same ID and compatible type.")
        self._synonyms = list(set(self._synonyms + other.synonyms))
        self._metadata.update(other._metadata)

    def replace_id(self,id):
        self._identifier = id
        
    @property
    def id(self):
        return self._identifier
    
    @property
    def type(self):
        return self._type
    
    def replace_type(self,type):
        if isinstance(type,TYPES):
            type = type.value
        self._type = type

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self,name):
        self._name = name

    @property
    def synonyms(self):
        return self._synonyms
    
    @property
    def confidence(self):
        return self._confidence
    
    @property
    def relationships(self):
        return self._relationships
    
    @confidence.setter
    def confidence(self,confidence):
        self._confidence = confidence
    
    def add_metadata(self,key,value):
        self._metadata[key] = value
    
    def add_synonym(self,value,source=None):
        if value not in self._synonyms:
            self._synonyms.append((value,source))

    def _init_relationship(self,relationship_type):
        self._relationships[relationship_type] = []

    def to_json(self):
        data = {"entity" : self.__class__.__name__,
                "type" : self._type,
                "id" : self._identifier,
                "name" : self._name,
                "synonyms" : self._synonyms,
                "relationships" : self._relationships,
                "metadata" : self._metadata,
                "confidence" : self._confidence}
        return data
    
    @classmethod
    def from_json(cls, data):
        # Determine the correct class
        obj_type = data.get("entity", "AbstractObject")
        target_cls = globals().get(obj_type, AbstractObject)

        # Pull core attributes
        identifier = data.get("id") or data.get("identifier")
        type_ = data.get("type")
        name = data.get("name")

        # Create object
        obj = target_cls(identifier, type_, name=name)

        # Restore optional properties
        if "confidence" in data:
            obj._confidence = data["confidence"]

        if "sequence" in data and hasattr(obj, "_sequence"):
            obj._sequence = data["sequence"]

        # Restore synonyms
        for synonym_pair in data.get("synonyms", []):
            if isinstance(synonym_pair, (list, tuple)) and len(synonym_pair) == 2:
                obj.add_synonym(synonym_pair[0], synonym_pair[1])
            else:
                obj.add_synonym(synonym_pair)

        # Restore metadata
        for k, v in data.get("metadata", {}).items():
            obj.add_metadata(k, v)

        # Restore relationships
        for rel_type, rel_entries in data.get("relationships", {}).items():
            obj._relationships[rel_type] = rel_entries

        return obj


class PhysicalEntity(AbstractObject):
    def __init__(self, identifier, type=None, name=None,
                 sequence=None,roles=None):
        super().__init__(identifier, type, name)
        self._sequence = sequence
        self._roles = roles if roles is not None else []
        self._init_relationship("contains")
    
    @property
    def sequence(self):
        return self._sequence
    
    @sequence.setter
    def sequence(self,sequence):
        self._sequence = sequence

    @property
    def roles(self):
        return self._roles
    
    @roles.setter
    def roles(self,role):
        if isinstance(role,TYPES):
            role = role.value
        if role not in self.roles:
            self.roles.append(role)
    
    @property
    def sub_regions(self):
        return self._relationships["contains"]

    def add_sub_region(self,identifier):
        if identifier not in self._relationships["contains"]:
            self._relationships["contains"].append(identifier)

    def merge(self, other):
        super().merge(other)
        self._roles = list(set(self._roles + other.roles))
        self._relationships["contains"] = list(set(self._relationships["contains"] + other._relationships["contains"]))
        

    def to_json(self):
        data = super().to_json()
        data["sequence"] = self._sequence
        data["roles"] = self._roles
        return data

class ConceptualEntity(AbstractObject):
    def __init__(self, identifier, type, name=None):
        super().__init__(identifier, type, name)
        self._init_relationship("participants")
    
    def add_participants(self,type,identifier):
        if isinstance(type,TYPES):
            type = type.value
        if (type,identifier) not in self._relationships["participants"]:
            self._relationships["participants"].append((type,identifier))
    
    @property
    def participants(self):
        return self._relationships["participants"]
    
    def merge(self, other):
        super().merge(other)
        self._relationships["participants"] = list(set(self._relationships["participants"] + 
                                                       other._relationships["participants"]))

class TYPES(Enum):
    GENE = "GENE"
    PROTEIN = "PROTEIN"
    RNA = "RNA"
    GENETICPRODUCTION = "GENETIC_PRODUCTION"
    TEMPLATE = "TEMPLATE"
    PRODUCT = "PRODUCT"
    OPERON = "OPERON"
    TRANSCRIPTIONUNIT = "TRANSCRIPTION_UNIT"
    TRANSCRIPTIONFACTOR = "TRANSCRIPTION_FACTOR"
    REGULATION = "REGULATION"
    DNA = "DNA"
    PROMOTER = "PROMOTER"
    REGULATED = "REGULATED"
    REGULATOR = "REGULATOR"
    ACTIVECONFORMATION = "ACTIVE_CONFORMATION"
    TRANSCRIPTIONINITIATION = "TRANSCRIPTIONINITIATION"
    INITIATOR = "INITIATOR"
    INITIATED = "INITIATED"
    SIGMAFACTOR = "SIGMAFACTOR"
    REPRESSION = "REPRESSION"
    ACTIVATION = "ACTIVATION"
    BINDINGSITE = "BINDING_SITE"

'''
class AbstractObject:
    def __init__(self,identifier,name=None,**kwargs):
        self.id = identifier
        self.name = name
        self._relationships = []
        self._properties = {}
        self._add_entity("name",name)
        self._properties.update(kwargs)
    

        





    def add_external_reference(self,identifier,
                               external_source=None):
        self._add_relationship("external",{"identifier" : identifier,
                                                 "source" : external_source})
    
    def add_internal_relationship(self,identifier,relationship=None):
        self._add_relationship("internal",{"identifier":identifier,
                                                 "relationship" : relationship})

    def add_functional_annotation(self, term_id, name=None, 
                                  source=None, label=None):
        term = {"id": term_id}
        if name:
            term["name"] = name
        if source:
            term["source"] = source
        if label:
            term["label"] = label
        self._add_properties("functional_annotation", term)

    def add_structural_annotation(self, annotation_type: str, 
                                  value: str, **kwargs):
        entry = {
            "type": annotation_type,
            "value": value
        }
        entry.update(kwargs)
        self._add_entities("structural_annotation", entry)

    def add_metadata(self,metadata):
        self._add_entity("metadata",metadata)
    
    def add_sequence(self,sequence):
        self._add_entity("sequence",sequence)

    def add_confidence(self,confidence):
        self._add_entity("confidence",confidence)

    def to_json(self):
        data = {"type" : self.__class__.__name__}
        data.update(self._data)
        return data
            
class ConceptualEntity(AbstractObject):
    def __init__(self, identifier, name=None, **kwargs):
        super().__init__(identifier, name, **kwargs)

    def add_type(self,type):
        self._add_entity("type",type)

    def add_role(self,role):
        self._add_entity("role",role)

    def add_structural_component(self, entity_id):
        self._add_entities("structural_components", entity_id)



class Gene(DNA):
    def __init__(self,identifier,name=None,**kwargs):
        super().__init__(identifier,name=name,**kwargs)
        self.add_role("Gene")

    def add_organism(self,identifier):
        self._add_entity("organism",identifier)
        
class Operon(DNA):
    def __init__(self,identifier,name=None,**kwargs):
        super().__init__(identifier,name=name,**kwargs)
        self.add_role("Operon")

    def add_transcription_unit(self,transcription_unit_id):
        self.add_internal_relationship(transcription_unit_id,"transcription_unit")



class TranscriptionUnit(AbstractObject):
    def __init__(self,identifier,name=None,**kwargs):
        super().__init__(identifier,name=name,**kwargs)

    def add_gene(self,gene_id):
        self.add_internal_relationship(gene_id,"gene")
        
class Interaction(AbstractObject):
    def __init__(self,identifier,name=None,**kwargs):
        super().__init__(identifier,name=name,**kwargs)

    def add_participant(self,identifier,type):
        self.add_internal_relationship(identifier,type)

class Regulation(Interaction):
    def __init__(self,identifier,name=None,**kwargs):
        super().__init__(identifier,name=name,**kwargs)

    def add_regulator(self,identifier):
        self.add_participant(identifier,"regulator")

    def add_regulated(self,identifier):
        self.add_participant(identifier,"regulated")

    def add_binding_site(self,identifier):
        self.add_internal_relationship(identifier,"binding_site")

    def add_active_conformation(self,identifier):
        self.add_internal_relationship(identifier,"active_conformation")

class TranscriptionInitiation(Interaction):
    def __init__(self, identifier, name=None, **kwargs):
        super().__init__(identifier, name, **kwargs)

    def add_initiator(self,identifier):
        self.add_participant(identifier,"initiator")

    def add_initiated(self,identifier):
        self.add_participant(identifier,"initiated")

class GeneticProduction(Interaction):
    def __init__(self, identifier, name=None, **kwargs):
        super().__init__(identifier, name, **kwargs)

    def add_product(self,identifier):
        self.add_participant(identifier,"product")

    def add_template(self,identifier):
        self.add_participant(identifier,"template")

'''