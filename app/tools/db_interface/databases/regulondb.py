import requests
import re

from app.tools.db_interface.databases.abstract_database import AbstractDatabase
from app.tools.db_interface.databases.abstract_database import PhysicalEntity
from app.tools.db_interface.databases.abstract_database import ConceptualEntity
from app.tools.db_interface.databases.abstract_database import TYPES

gene_query_body = """
data {
  gene {
    _id
    name
    bnumber
    strand
    leftEndPosition
    rightEndPosition
    centisomePosition
    gcContent
    synonyms
    sequence
    externalCrossReferences {
      externalCrossReferenceName
      objectId
    }
    multifunTerms {
      _id
      name
      label
    }
  }
  products {
    _id
    name
    molecularWeight
    synonyms
    sequence
    externalCrossReferences {
      externalCrossReferenceName
      objectId
    }
    geneOntologyTerms {
      biologicalProcess {
        name
      }
      molecularFunction {
        name
      }
      cellularComponent {
        name
      }
    }
    motifs {
      _id
      type
      sequence
      leftEndPosition
      rightEndPosition
      note
      dataSource
    }
  }
  regulation {
    operon {
      _id
    }
  }
  organism {
    _id
  }
}
"""

CONFIDENCE_SCORE_MAP = {
    "S": 1.0,  # Strong evidence
    "M": 0.7,  # Medium (if present; not always used)
    "W": 0.4,  # Weak evidence
    "N": 0.2,  # Not enough evidence
    "Q": 0.1,  # Questionable or predicted
    "ND": 0.0,  # No data
    None: 0.0,
}


class RegulonDB(AbstractDatabase):
    BASE_URL = "https://regulondb.ccg.unam.mx/graphql"

    def __init__(self):
        self.session = requests.Session()

    def _post(self, graphql_query: str):
        """Send a POST request with a GraphQL query to RegulonDB."""
        try:
            response = self.session.post(
                self.BASE_URL, json={"query": graphql_query}, verify=False
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"GraphQL API call failed: {e} {response.text}")

    def fetch_all(self):
        """Fetch all core biological entities."""
        all_data = {}

        genes = self.fetch_all_genes(30)
        for gene in genes:
            all_data = self._process_gene(gene,all_data)

        operons = self.fetch_all_operons(30)
        for operon in operons:
            all_data = self._process_operon(operon,all_data)
       
        regulons = self.fetch_all_regulons(30)
        for regulon in regulons:
            all_data = self._process_regulon(regulon,all_data)
        
        sigmulons = self.fetch_all_sigmulons(30)
        for sigmulon in sigmulons:
            all_data = self._process_sigmulon(sigmulon,all_data)

        return list(all_data.values())

    
    def fetch_entity(self, identifier: str, type: str):
        """Fetch a single entity overview by name."""
        query = f"""
        {{
          getGenesBy(search:"{identifier}"){{
            {gene_query_body}
          }}
        }}
        """
        res = self._post(query)
        return res["data"]["getGenesBy"]["data"]

    # ---- High Level Processors ----
    def _process_gene(self, gene, all_data):
        gene_data = gene["gene"]
        products = gene["products"]
        regulations = gene["regulation"]
        organism = gene["organism"]

        new_gene = PhysicalEntity(gene_data.pop("_id"),
                                    TYPES.GENE, 
                                    name=gene_data.pop("name"),
                                    sequence=gene_data.pop("sequence"))
        self._add_external_references(
            new_gene,
            gene_data.pop("synonyms"),
            gene_data.pop("externalCrossReferences"),
        )

        for term in gene_data.pop("multifunTerms", []):
            new_gene.add_metadata(
                term["_id"],
                {"name":term["name"],
                "label":term.get("label"),
                "source":"MultiFun"}
            )

        for product in products:
            obj,all_data = self._process_product(product,all_data)
            product_id = f'{new_gene.id} - {obj.id}'
            product_name = f'{new_gene.name} - Produces - {obj.name}'

            product_i = ConceptualEntity(product_id,
                                         TYPES.GENETICPRODUCTION,
                                         product_name)

            product_i.add_participants(TYPES.PRODUCT,obj.id)
            product_i.add_participants(TYPES.TEMPLATE,new_gene.id)
            
            all_data[obj.id] = obj
            all_data[product_i.id] = product_i

        if regulations is not None:
            pass # AQUI - is this handled in the operons part????
            #new_gene.add_operon(regulations["operon"]["_id"])

        new_gene.add_metadata("organism",organism["_id"])
        for k,v in gene_data.items():
          new_gene.add_metadata(k,v)

        all_data[new_gene.id] = new_gene
        return all_data

    def _process_operon(self, data, all_data):
        operon_data = data["operon"]

        operon = PhysicalEntity(operon_data.pop("_id"),TYPES.OPERON, 
                                operon_data["name"])
        for k,v in operon_data.items():
          operon.add_metadata(k,v)

        for tu_data in data["transcriptionUnits"]:
            tu_id = tu_data.pop("_id")
            operon.add_sub_region(tu_id)
            tu = PhysicalEntity(tu_id,TYPES.TRANSCRIPTIONUNIT, 
                                tu_data.pop("name"))
            confidence = self._map_confidence(tu_data.pop("confidenceLevel"))
            tu.confidence = confidence

            for gene in tu_data.pop("genes"):
                gene_id = gene.pop("_id")
                tu.add_sub_region(gene_id)
                if gene_id not in all_data:
                    existing_gene = self.fetch_entity(gene_id, "Gene")
                    assert len(existing_gene) == 1
                    all_data = self._process_gene(existing_gene[0], all_data)
                    existing_gene = all_data[gene_id]
                else:
                    existing_gene = all_data[gene_id]

                for bs in gene["regulatorBindingSites"]:
                    regulator = bs.pop("regulator", {})
                    regulator_id, all_data = self._ensure_protein(regulator, all_data)
                    for interaction_data in bs.pop("regulatoryInteractions", []):
                        all_data = self._process_regulatory_interaction(
                            interaction_data, gene_id, regulator_id, all_data
                        )

            all_data[tu_id] = tu

        all_data[operon.id] = operon
        return all_data

    def _process_regulon(self,regulon,all_data):
        regulator_data = regulon.pop("regulator")
        regulator = self._make_regulator(regulator_data, all_data)
        all_data = self._add_entity(regulator,all_data)

        regulatory_interactions = regulon.pop("regulatoryInteractions")
        for interaction_data in regulatory_interactions:
            
            interaction_id = interaction_data.pop("_id")
            interaction_function = interaction_data.pop("function")
            if interaction_function == "repressor":
                interaction_type = TYPES.REPRESSION
            elif interaction_function == "activator":
                interaction_type = TYPES.ACTIVATION
            else:
                raise ValueError(interaction_type)
            interaction = ConceptualEntity(interaction_id,
                                           interaction_type, 
                                           interaction_function)
            
            confidence = self._map_confidence(interaction_data.pop("confidenceLevel"))
            interaction.confidence = confidence
            
            regulated_data = interaction_data.pop("regulatedEntity")

            regulated = PhysicalEntity(regulated_data.pop("_id"),
                                       TYPES.DNA,
                                       regulated_data.pop("name"))
            regulated_type = regulated_data.pop("type")
            
            all_data = self._add_entity(regulated,all_data)
            interaction.add_participants(TYPES.REGULATED,regulated.id)
            interaction.add_participants(TYPES.REGULATOR,regulator.id)
            
            # Set the interaction with the regulatedEntity
            ac_data = interaction_data.pop("activeConformation", None)
            if ac_data:
                ac_id = ac_data.pop("_id")
                if ac_id != regulator.id:
                  raise ValueError("Think about this when you find one.")
                  ac = PhysicalEntity(ac_data.pop("_id"),
                                      ac_data.pop("type", ""),
                                      ac_data.pop("name"))
                  all_data = self._add_entity(ac, all_data)
                  interaction.add_participants(TYPES.ACTIVECONFORMATION,ac.id)

            all_data = self._add_entity(interaction,all_data)
            for gene_data in interaction_data.pop("regulatedGenes"):
                if regulated_type == "promoter":
                    regulated.replace_type(TYPES.PROMOTER)

                    gene = PhysicalEntity(gene_data.pop("_id"),
                                          TYPES.GENE,
                                          gene_data.pop("name"))
                    all_data = self._add_entity(gene,all_data)
                    all_data = self._add_transcription_initiation(regulated,gene,all_data)

                elif regulated_type == "transcriptionUnit":
                    regulated.replace_type(TYPES.TRANSCRIPTIONUNIT)
                    gene = PhysicalEntity(gene_data.pop("_id"),
                                          TYPES.GENE, 
                                          gene_data.pop("name"))
                    for k,v in gene_data.items():
                      gene.add_metadata(k,v)
                    all_data = self._add_entity(gene, all_data)
                    regulated.add_sub_region(gene.id)
                elif regulated_type == "gene":
                    regulated.replace_type(TYPES.GENE)
                    assert(regulated.id == gene_data["_id"])
                    # I dont know what this means. My current thought is that its just wrong in regulonDB.
                else:
                    # Gonna leave this here until i run it properly and figure out what the data might be.
                    raise ValueError(regulated_type)
        return all_data
                
    def _process_sigmulon(self,sigmulon,all_data):
        sigma_factor = sigmulon.pop("sigmaFactor")
        sig_protein = PhysicalEntity(sigma_factor.pop("_id"),
                                     TYPES.PROTEIN,
                                     sigma_factor.pop("name"))
        sig_protein.roles = TYPES.SIGMAFACTOR
        for s in sigma_factor.pop("synonyms"):
            sig_protein.add_synonym(s)
        all_data = self._add_entity(sig_protein,all_data)
        
        sfs_data = sigma_factor.pop("gene")
        sigma_factor_source = PhysicalEntity(sfs_data.pop("_id"),
                                             TYPES.GENE,
                                             sfs_data.pop("name"))
        all_data = self._add_entity(sigma_factor_source,all_data)
        
        gp_id = f'{sigma_factor_source.id} - {sig_protein.id}'
        gp_name = f'{sigma_factor_source.name} - Produces - {sig_protein.name}'
        gp = ConceptualEntity(gp_id,TYPES.GENETICPRODUCTION,gp_name)
        gp.add_participants(TYPES.PRODUCT,sig_protein.id)
        gp.add_participants(TYPES.TEMPLATE,sigma_factor_source.id)
        all_data = self._add_entity(gp,all_data)


        for promoter_data in sigmulon.pop("transcribedPromoters"):
            promoter = PhysicalEntity(promoter_data.pop("_id"),
                                      TYPES.PROMOTER,
                                      promoter_data.pop("name"))
            promoter.sequence = promoter_data.pop("sequence")
            for k,v in promoter_data.items():
              promoter.add_metadata(k,v)
            all_data = self._add_entity(promoter,all_data)
            for gene_data in promoter_data.pop("transcribedGenes"):
                gene = PhysicalEntity(gene_data.pop("_id"),
                                      TYPES.GENE,
                                      gene_data.pop("name"))
                all_data = self._add_transcription_initiation(promoter,gene,all_data)
                all_data = self._add_entity(gene,all_data)
        return all_data
    

    def _make_regulator(self, data, all_data):
        reg_id  = data.pop("_id")
        name    = data.pop("name")
        r_type  = data.pop("type", "").lower()

        c_type = TYPES.PROTEIN if r_type.startswith(("protein", "transcriptionfactor", "tf")) else TYPES.TRANSCRIPTIONFACTOR

        if reg_id in all_data:
            return all_data[reg_id]

        reg = PhysicalEntity(reg_id,c_type,name)
        for syn in data.pop("synonyms", []):
            reg.add_synonym(syn)
        if r_type != "":
            reg.roles = r_type
        all_data[reg_id] = reg
        return reg

    def _add_entity(self,entity,all_data):
        if entity.id not in all_data:
            all_data[entity.id] = entity
        else:
            all_data[entity.id].merge(entity) 
        return all_data
    
    def _infer_sequence_type(self, sequence: str) -> str:
        """
        Infer the type of a biological sequence.
        Returns one of: 'RNA', 'DNA', 'Protein', or 'Unknown'
        """
        if not sequence or not isinstance(sequence, str):
            return None

        seq = sequence.upper().strip()

        # Remove any whitespace or HTML entities if they slipped in
        seq = re.sub(r"[^A-Z]", "", seq)

        # RNA: contains U, and only RNA nucleotide letters
        if re.fullmatch(r"[ACGU]+", seq):
            return TYPES.RNA

        # DNA: contains T, but not U, and only DNA nucleotides
        if "T" in seq and "U" not in seq and re.fullmatch(r"[ACGT]+", seq):
            return TYPES.GENE

        # Protein: contains letters outside nucleotide set
        protein_letters = set("ACDEFGHIKLMNPQRSTVWY")
        nucleotide_letters = set("ACGTU")
        unique_letters = set(seq)

        if unique_letters.issubset(protein_letters) and not unique_letters.issubset(
            nucleotide_letters
        ):
            return TYPES.PROTEIN

        raise ValueError()

    def _add_external_references(self, entity, synonyms, cross_refs):
        seen = set()
        for ref in cross_refs:
            res_name = ref["externalCrossReferenceName"]
            obj_id = ref["objectId"]
            entity.add_synonym(obj_id, res_name)
            seen.add(obj_id)

        for syn in synonyms:
            if syn not in seen:
                entity.add_synonym(syn)

    def _process_product(self, data, all_data):
        p_id = data.pop("_id")
        name = data.pop("name")
        sequence = data.pop("sequence")
        p_type = self._infer_sequence_type(sequence)

        obj = PhysicalEntity(p_id,p_type,name)
        self._add_external_references(obj, data.pop("synonyms"), 
                                      data.pop("externalCrossReferences"))

        ontology = data.pop("geneOntologyTerms")
        for term_group in ("biologicalProcess", "molecularFunction"):
            for item in ontology.get(term_group, []):
                code, name = item["name"].split(" - ", 1)
                obj.add_metadata(code.strip(),{"name":name.strip(), 
                                               "source":"GO"})

        for m in data["motifs"]:
            motif = PhysicalEntity(m.pop("_id"),p_type, m.pop("type"))
            motif.sequence = m.pop("sequence")
            for k,v in m.items():
                motif.add_metadata(k,v)
            obj.add_sub_region(motif.id)
            all_data = self._add_entity(motif,all_data)

        return obj,all_data

    def _map_confidence(self, level: str) -> float:
        return CONFIDENCE_SCORE_MAP.get(level, 0.0)

    def _ensure_protein(self, protein_data, all_data):
        prot_id = protein_data.pop("_id")
        name = protein_data.pop("name")
        tf = PhysicalEntity(prot_id,TYPES.PROTEIN, name)
        all_data = self._add_entity(tf,all_data)
        return prot_id, all_data

    def _process_regulatory_interaction(
        self, interaction_data, gene_id, regulator_id, all_data
    ):
        interaction_id = interaction_data.pop("_id")
        interaction_function = interaction_data.pop("function")
        if interaction_function == "repressor":
            interaction_type = TYPES.REPRESSION
        elif interaction_function == "activator":
            interaction_type = TYPES.ACTIVATION
        else:
            raise ValueError(interaction_type)
        interaction = ConceptualEntity(interaction_id,
                                        interaction_type, 
                                        interaction_function)

        confidence = self._map_confidence(interaction_data.pop("confidenceLevel"))
        interaction.confidence = confidence

        reg_site = interaction_data.get("regulatorySite", {})
        if reg_site:
            reg_dna = PhysicalEntity(reg_site.pop("_id"),
                                     TYPES.DNA, 
                                     reg_site.pop("note", None))
            reg_dna.sequence = reg_site.pop("sequence", None)
            all_data = self._add_entity(reg_dna,all_data)
            all_data[reg_dna.id] = reg_dna
            interaction.add_participants(TYPES.BINDINGSITE,reg_dna.id)

        interaction.add_participants(TYPES.REGULATED,regulator_id)
        interaction.add_participants(TYPES.REGULATOR,gene_id)
        all_data[interaction_id] = interaction

        return all_data

    def _add_transcription_initiation(self,promoter,gene,all_data):
        
        ti_id = f'{promoter.id}-{gene.id}'
        ti_name = f'{promoter.name} initiates {gene.name}'
        interaction = ConceptualEntity(ti_id,TYPES.TRANSCRIPTIONINITIATION,
                                       ti_name)
        interaction.add_participants(TYPES.INITIATOR,promoter.id)
        interaction.add_participants(TYPES.INITIATED,gene.id)
        all_data = self._add_entity(interaction,all_data)
        return all_data
    
  # ----- Fetchers -----
    def fetch_all_genes(self, limit: int = 1000):
        """Fetch all genes with biologically relevant attributes."""
        query = f"""
        {{
          getAllGenes(limit: {limit}) {{ 
            {gene_query_body}
            }}
        }}
        """
        res = self._post(query)
        return res["data"]["getAllGenes"]["data"]

    def fetch_all_operons(self, limit: int = 1000):
        """Fetch all operons with structure and regulation info."""
        query = f"""
        {{
          getAllOperon(limit: {limit}) {{
            data {{
              operon {{
                _id
                name
                strand
                regulationPositions {{
                  leftEndPosition
                  rightEndPosition
                }}
              }}
              transcriptionUnits {{
                _id
                name
                confidenceLevel
                genes {{
                  _id
                  name
                  regulatorBindingSites {{
                    function
                    regulator {{
                      _id
                      name
                    }}
                    regulatoryInteractions {{
                      _id
                      function
                      confidenceLevel
                      regulatorySite{{
                        _id
                        sequence
                        note  
                      }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
        """
        res = self._post(query)
        return res["data"]["getAllOperon"]["data"]

    def fetch_all_regulons(self, limit: int = 1000):
        """Fetch all regulons with essential fields for building regulatory graph."""
        query = f"""
        {{
          getAllRegulon(limit: {limit}) {{
            data {{
              _id
              regulator {{
                _id
                name
                synonyms
                type
              }}
              regulates {{
                genes {{
                  _id
                  name
                }}
                operons {{
                  _id
                  name
                }}
              }}
            regulatoryInteractions {{
            _id
            confidenceLevel
            function
            regulatedEntity {{
                _id
                name
                type
            }}
            regulatedGenes {{
                _id
                name
                leftEndPosition
                rightEndPosition
             }}
            activeConformation {{
                _id
                name
                type
             }}
             }}
              }}
            }}
          }}
        """
        res = self._post(query)
        return res["data"]["getAllRegulon"]["data"]

    def fetch_all_sigmulons(self, limit: int = 1000):
        """Fetch all sigmulons with sigma factor, target genes, and transcribed promoters."""
        query = f"""
        {{
          getAllSigmulon(limit: {limit}) {{
            data {{
              _id
              sigmaFactor {{
                _id
                name
                synonyms
                gene {{
                  _id
                  name
                }}
              }}
              transcribedPromoters {{
                _id
                name
                TSSPosition
                strand
                sequence
                transcribedGenes {{
                  _id
                  name
                }}
              }}
            }}
          }}
        }}
        """
        res = self._post(query)
        return res["data"]["getAllSigmulon"]["data"]
