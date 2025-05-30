#  Multimodal Knowledge Graphs for Systems Biology Inference

## Project Overview

This project aims to integrate multimodal biological datasets into a **semantically rich, multi-layered knowledge graph** representing the molecular network of a model organism (e.g., *E. coli* or *S. cerevisiae*). The goal is to apply **network science and systems biology techniques** to:

- Infer missing or uncertain biological interactions,
- Identify conserved or functional **network motifs**,
- Simulate **dynamic behavior** under various perturbations.

The project is designed as a **learning-first exploration**, with the potential to produce novel findings or reusable tools for the community.

---

##  Project Objectives

https://drive.google.com/file/d/1jL8ur9Vg2w8Dz0y9rAj7NZ1PSXlbaKDg/view?usp=drive_link

### Phase 1: Data Acquisition & Standardization
Extract and stage biological datasets from diverse sources.
Apply consistent structure, normalize identifiers, and annotate with metadata.
Input: A specific organism name (E.coli etc). 
Output:  semantically enriched, graph-ready data such as an RDF file.

#### Tasks
1. Write interfaces to extract data from:
   1. RegulonDB
      1. What: TF-gene interactions, operon structure, conditions.
      2. How: Use RegulonDB API. Alternatively, download flat files (JSON, TSV)
      3. Key Entities: TFs, genes, regulation type (activation/inhibition), evidence level, growth condition.
   2. STRING
      1. What: Protein-protein interaction scores (functional + physical).
      2. How: Use their REST API or download TSVs.
         1. Python wrapper: bioservices.STRING
      3. Key Entities: proteins, combined score, sources (experimental, co-expression, etc.)
   3. BioGRID
      1. What: Physical and genetic interactions.
      2. How: Download from BioGRID FTP
      3. Key Entities: interactor A/B, interaction type, detection method.
   4. GEO
      1. What: Gene expression data (microarray/RNA-seq).
      2. How:Use GEOparse or pandas + Entrez.
      3. Key Entities: gene IDs, expression values, sample metadata (condition, strain, etc.)
   5. ArrayExpress
      1. What: Expression + other omics data.
      2. How: Use bioservices.ArrayExpress
      3. Key Entities: same as GEO, often better sample annotation.
   6. KEGG
      1. What: Pathway maps, reaction networks, gene-pathway mapping.
      2. How: Use bioservices.KEGG.
      3. Key Entities: enzymes, reactions, pathways, KO terms.
   7. BioCyc
      1. What: Metabolic and regulatory pathways.
      2. How: API access (requires registration) or download flat files.
      3. Key Entities: same as KEGG, often better for regulatory detail.
2. Define the semantics
   1. By looking at the entities which come from the DB's define some semantics.
   2. This could be a good place to dig into true knowledge graph stuff. I.e. how do people actually come up with a set of terms and relationships?
   3. Identify key entity types (Gene, Protein, Pathway, TF, Sample, Condition, etc.)
   2. Define relationship types (regulates, encodes, interacts_with, expressed_in, part_of, etc.)
   3. Determine required/optional attributes per type (e.g., gene → symbol, Entrez ID, organism)
   4. Optionally: map to existing vocabularies (Biolink Model, GO, SIO, etc.)
   5. Create a schema config (YAML/JSON/Python class) for use during data ingestion
3. Canonicalize & Transform Data into Network Representation
   0. Have a think if to use rdflib from the get go, or just after stuff has been proceded, i.e. once we know it wont change (use pandas etc) otherwise.
   1. Normalize Identifiers
      1. Ensure consistent and canonical representation of biological entities:
         1. Canonicalize Identifiers: Map all aliases (e.g., lacZ, b0344, P00722) to a unified ID system (e.g., UniProt).
      2. Assign Type + Properties: For each entity, assign a semantic type (Gene, Protein, etc.) and attach any core attributes per the schema.
   2. Parse & Standardize Metadata
      1. Extract Fields: From dataset headers, descriptions, files.
      2. Normalize Values: Use lookup tables, controlled vocabularies, regex, etc.
      3. Encode Consistently: Store in a way compatible with the graph schema (attributes on nodes/edges, additional metadata nodes, etc.)
   3. Store Raw & Processed Data
      1. Essentially archive it. So then you can access it later. 
      2. Note, doesnt have to be done here. Can be done throughout.
   4. Extras (Dont know where these would be done yet)
      1. Track provenance of each edge: where it came from, what kind of evidence.

### Phase 2: Knowledge Graph Construction
- Input: Semantically normalized data from Phase 1
  - Format: Could be RDF (.ttl), JSON-LD, CSV triples, or tabular files with semantic columns
- Output: Fully instanced graph in Neo4j or another backend

#### Tasks:
1. Load data into Neo4j (or other KG engine)
   - Convert RDF to Cypher import
   - Use APOC procedures or `neomodel`/`py2neo` for programmatic ingestion
2. Apply type constraints / labels
   - Label nodes by type: `:Gene`, `:Protein`, `:TF`, etc.
   - Assign properties per schema
3. Validate relationships and provenance
   - Ensure only defined edge types exist
   - Confirm edge attributes (evidence, source, etc.)
4. Optional: Generate Graph Indexes
   - For performance in later querying/analysis

### Phase 3: Network Science Analysis
- **Motif discovery** (feed-forward loops, bi-fans, etc.)
- **Missing interaction prediction** using:
  - Embedding-based methods (Node2Vec, GraphSAGE)
  - Probabilistic or graph-based inference
- Community/module detection for functional annotation.

###  Phase 4: Dynamic Modeling (Stretch Goal)
- Simulate key subnetworks using:
  - **SBML**, **Tellurium**, **COPASI**, or **PySB**
- Explore knockout experiments, time series, and perturbation effects.

###  Phase 5: Visualization & Dissemination
- Visualize multi-layer networks using:
  - **Cytoscape.js**, **D3.js**, or **Neo4j Bloom**
- Develop a sharable interactive dashboard or report.
- Optionally package as a reusable toolkit or template.

---

## Tools & Tech Stack

- **Languages**: Python (NetworkX, Pandas, RDFLib), R (optional)
- **Databases**: Neo4j, Blazegraph, or graph file formats (GraphML, JSON-LD)
- **Visualization**: Cytoscape, Cytoscape.js, D3.js
- **Simulation**: Tellurium, COPASI, BioNetGen, SBML
- **Standards**: SBML, SBOL, OBO ontologies, Biolink Model

---

## Novelty Potential

- Cross-modal, **context-aware integration** of biological networks
- Combining **motif inference**, **link prediction**, and **dynamic modeling**
- Emphasis on **metadata provenance** and **semantic richness**
- Toolchain could be generalized and shared for community use

---
