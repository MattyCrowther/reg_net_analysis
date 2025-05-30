from os import name
from rdflib import URIRef,RDF,Literal

class Identifiers:
    def __init__(self):
        self.namespaces = Namespace()
        self.predicates = Predicates(self.namespaces)
        self.roles = Roles(self.namespaces)
    
class Namespace:
    def __init__(self):
        identifiers = URIRef('http://identifiers.org/')
        self.nv = URIRef("http://www.nv_ontology.org/")
        self.sequence_ontology = URIRef(identifiers + 'so/SO:')
        self.sbo_biomodels = URIRef(identifiers + 'biomodels.sbo/SBO:') 
        self.identifier_edam = URIRef(identifiers + 'edam/')
        self.biopax = URIRef('http://www.biopax.org/release/biopax-level3.owl#')
        self.dc = URIRef('http://purl.org/dc/terms/')
        self.edam = URIRef('http://edamontology.org/')
        self.edam_format = URIRef(self.edam + "format")
        self.prov = URIRef('http://www.w3.org/ns/prov#')
        self.efo = URIRef("http://www.ebi.ac.uk/efo/EFO")
        self.obi = URIRef("http://purl.obolibrary.org/obo/OBI")

class Predicates:
    def __init__(self, namespaces):
        namespaces = namespaces
        self.rdf_type = URIRef(RDF.type)
        self.synonym = URIRef("http://purl.obolibrary.org/obo/NCIT_C52469")

class Roles:
    def __init__(self, namespaces):
        namespaces = namespaces

        self.physical_entity     = [Literal("PHYSICAL_ENTITY"), URIRef(namespaces.biopax + "PhysicalEntity")]
        self.conceptual_entity   = [Literal("INTERACTION"), URIRef(namespaces.biopax + "Interaction")]

        self.DNA                 = [Literal("DNA"), URIRef(namespaces.biopax + "Dna")]
        self.DNARegion           = [Literal("DNA_REGION"), URIRef(namespaces.biopax + "DnaRegion")]
        self.RNA                 = [Literal("RNA"), URIRef(namespaces.biopax + "Rna")]
        self.RNARegion           = [Literal("RNA_REGION"), URIRef(namespaces.biopax + "RnaRegion")]
        self.protein             = [Literal("PROTEIN"), URIRef(namespaces.biopax + "Protein")]
        self.smallMolecule       = [Literal("SMALL_MOLECULE"), URIRef(namespaces.biopax + "SmallMolecule")]
        self.complex             = [Literal("COMPLEX"), URIRef(namespaces.biopax + "Complex")]
        self.all                 = [Literal("ALL_TYPE"), URIRef("http://www.placeholder.com/all_type")]

        # Sequence ontology
        self.promoter            = [Literal("PROMOTER"), URIRef(namespaces.sequence_ontology + "0000167")]
        self.rbs                 = [Literal("RBS"), URIRef(namespaces.sequence_ontology + "0000139")]
        self.cds                 = [Literal("CDS"), URIRef(namespaces.sequence_ontology + "0000316")]
        self.terminator          = [Literal("TERMINATOR"), URIRef(namespaces.sequence_ontology + "0000141")]
        self.gene                = [Literal("GENE"), URIRef(namespaces.sequence_ontology + "0000704")]
        self.operator            = [Literal("OPERATOR"), URIRef(namespaces.sequence_ontology + "0000057")]
        self.engineeredGene      = [Literal("ENGINEERED_GENE"), URIRef(namespaces.sequence_ontology + "0000280")]
        self.mRNA                = [Literal("MRNA"), URIRef(namespaces.sequence_ontology + "0000234")]
        self.engineeredRegion    = [Literal("ENGINEERED_REGION"), URIRef(namespaces.sequence_ontology + "0000804")]
        self.nonCovBindingSite   = [Literal("NON_COVALENT_BINDING_SITE"), URIRef(namespaces.sequence_ontology + "0001091")]
        self.effector            = [Literal("EFFECTOR"), URIRef("http://identifiers.org/chebi/CHEBI:35224")]
        self.startCodon          = [Literal("START_CODON"), URIRef(namespaces.sequence_ontology + "0000318")]
        self.tag                 = [Literal("TAG"), URIRef(namespaces.sequence_ontology + "0000324")]
        self.engineeredTag       = [Literal("ENGINEERED_TAG"), URIRef(namespaces.sequence_ontology + "0000807")]
        self.sgRNA               = [Literal("SGRNA"), URIRef(namespaces.sequence_ontology + "0001998")]
        self.transcriptionFactor = [Literal("TRANSCRIPTION_FACTOR"), URIRef("http://identifiers.org/go/GO:0003700")]
        self.transcriptionUnit   = [Literal("TRANSCRIPTION_UNIT"), URIRef("http://identifiers.org/go/GO:0000185")]
        self.operon              = [Literal("OPERON"), URIRef("http://identifiers.org/go/GO:0000178")]

        # SBO processes
        self.inhibition              = [Literal("INHIBITION"),Literal("REPRESSION"), URIRef(namespaces.sbo_biomodels + "0000169")]
        self.stimulation             = [Literal("STIMULATION"),Literal("ACTIVATION"), URIRef(namespaces.sbo_biomodels + "0000170")]
        self.biochemical_reaction    = [Literal("BIOCHEMICAL_REACTION"), URIRef(namespaces.sbo_biomodels + "0000176")]
        self.noncovalent_bonding     = [Literal("NONCOVALENT_BONDING"), URIRef(namespaces.sbo_biomodels + "0000177")]
        self.association             = [Literal("COMPLEX_ASSEMBLY"), URIRef(namespaces.biopax + "ComplexAssembly")]
        self.degradation             = [Literal("DEGRADATION"), URIRef(namespaces.sbo_biomodels + "0000179")]
        self.genetic_production      = [Literal("GENETIC_PRODUCTION"), URIRef(namespaces.sbo_biomodels + "0000589")]
        self.control                 = [Literal("CONTROL"), URIRef(namespaces.sbo_biomodels + "0000168")]
        self.transcription           = [Literal("TRANSCRIPTION"),
                                        Literal("TRANSCRIPTIONINITIATION"), 
                                        URIRef(namespaces.sbo_biomodels + "0000183")]

        # SBO roles
        self.inhibitor               = [Literal("INHIBITOR"), 
                                        Literal("REGULATOR"),
                                        URIRef(namespaces.sbo_biomodels + "0000020")]
        self.inhibited               = [Literal("INHIBITED"), 
                                        Literal("REGULATED"), 
                                        URIRef(namespaces.sbo_biomodels + "0000642")]
        self.stimulator              = [Literal("STIMULATOR"),
                                        Literal("REGULATOR"),
                                        Literal("INITIATOR"), 
                                        URIRef(namespaces.sbo_biomodels + "0000459")]
        self.stimulated              = [Literal("STIMULATED"),
                                        Literal("REGULATED"),
                                        Literal("INITIATED"), 
                                        URIRef(namespaces.sbo_biomodels + "0000643")]
        self.modifier                = [Literal("MODIFIER"), URIRef(namespaces.sbo_biomodels + "0000019")]
        self.modified                = [Literal("MODIFIED"), URIRef(namespaces.sbo_biomodels + "0000644")]
        self.product                 = [Literal("PRODUCT"), URIRef(namespaces.sbo_biomodels + "0000011")]
        self.reactant                = [Literal("REACTANT"), URIRef(namespaces.sbo_biomodels + "0000010")]
        self.template                = [Literal("TEMPLATE"), URIRef(namespaces.sbo_biomodels + "0000645")]
        self.interaction_binding_site = [Literal("BINDING_SITE")]

        # More SBO processes
        self.translation             = [Literal("TRANSLATION"), URIRef(namespaces.sbo_biomodels + "0000184")]
        
        self.dissociation            = [Literal("DISSOCIATION"), URIRef(namespaces.sbo_biomodels + "0000180")]
        self.hydrolysis              = [Literal("HYDROLYSIS"), URIRef(namespaces.sbo_biomodels + "0000376")]



        self.synonym = URIRef("http://purl.obolibrary.org/obo/NCIT_C52469")
identifiers = Identifiers()