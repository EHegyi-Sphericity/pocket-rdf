# CGMES Examples

These examples demonstrate pocketRDF's primary use case: **validating and querying
CGMES (Common Grid Model Exchange Standard) datasets** used in the European
power system industry.

CGMES datasets consist of multiple RDF/XML files, each representing a distinct
profile (Equipment, Topology, State Variables, etc.). pocketRDF loads each file
into its own named graph (`--dataset`), enabling profile-aware validation and
querying.

## Prerequisites

### 1. Install pocketRDF

```bash
pip install .
```

### 2. Download CGMES Test Models

The test models are published by ENTSO-E and are **not included** in this
repository. Download them from:

**CGMES v2.4.15 Test Configurations:**
https://www.entsoe.eu/Documents/CIM_documents/Grid_Model_CIM/TestConfigurations_packageCASv2.0.zip

After downloading:

1. Extract the ZIP file
2. Copy the XML files from a test configuration (e.g.,
   `MiniGrid\NodeBreaker\CGMES_v2.4.15_MiniGridTestConfiguration_BaseCase_Complete_v3.zip`
   and
   `MiniGrid\NodeBreaker\CGMES_v2.4.15_MiniGridTestConfiguration_Boundary_v3.zip`)
   into the `models/` directory

Example directory structure after setup:

```
examples/cgmes/
├── adapted_cgmes_2_4_15_shacl/   ← SHACL shapes (included)
├── models/                        ← CGMES XML files (you provide)
│   ├── MiniGridTestConfiguration_BC_DL_v3.0.0.xml
│   ├── MiniGridTestConfiguration_BC_EQ_v3.0.0.xml
│   ├── MiniGridTestConfiguration_BC_SSH_v3.0.0.xml
│   ├── MiniGridTestConfiguration_BC_SV_v3.0.0.xml
│   ├── MiniGridTestConfiguration_BC_TP_v3.0.0.xml
│   ├── MiniGridTestConfiguration_EQ_BD_v3.0.0.xml
│   ├── MiniGridTestConfiguration_TP_BD_v3.0.0.xml
│   └── ...
├── queries/                       ← SPARQL queries (included)
└── output/                        ← Generated output (git-ignored)
```

## Queries

| File | Description |
|------|-------------|
| `queries/list_model_headers.sparql` | List FullModel headers from each profile. |
| `queries/count_triples_per_graph.sparql` | Count triples per named graph (profile). |
| `queries/list_types_per_graph.sparql` | List CIM types and instance counts per profile. |
| `queries/list_substations.sparql` | List all Substations with name and region. |
| `queries/list_acline_segments.sparql` | List ACLineSegments with length and resistance. |

## SHACL Shapes

The `adapted_cgmes_2_4_15_shacl/` directory contains SHACL shapes adapted for
CGMES v2.4.15 profiles, originally licensed by ENTSO-E under the Apache License 2.0 (see
`LICENSE.txt` and `NOTICE.txt`).

| Shape file | CGMES Profile |
|------------|---------------|
| `EquipmentProfile.ttl` | Equipment (EQ) |
| `EquipmentBoundaryProfile.ttl` | Equipment Boundary (EQ_BD) |
| `TopologyProfile.ttl` | Topology (TP) |
| `TopologyBoundaryProfile.ttl` | Topology Boundary (TP_BD) |
| `SteadyStateHypothesisProfile.ttl` | Steady State Hypothesis (SSH) |
| `StateVariablesProfile.ttl` | State Variables (SV) |
| `DiagramLayoutProfile.ttl` | Diagram Layout (DL) |
| `GeographicalLocationProfile.ttl` | Geographical Location (GL) |
| `FileHeaderProfile.ttl` | File Header / Model Description |

---

## Serialize CGMES Data

Convert the dataset to TriG format (preserving named graphs):

```bash
pocket-rdf serialize models/*.xml \
  --dataset \
  --out output/cgmes_dataset.trig
```

## Query CGMES Data

Inspect model headers to verify which profiles are present:

```bash
pocket-rdf query models/*.xml \
  --dataset \
  --query queries/list_model_headers.sparql \
  --out output/model_headers.json
```

Count triples per profile:

```bash
pocket-rdf query models/*.xml \
  --dataset \
  --query queries/count_triples_per_graph.sparql \
  --out output/triples_per_graph.csv
```

List all substations:

```bash
pocket-rdf query models/*.xml \
  --dataset \
  --query queries/list_substations.sparql \
  --out output/substations.json
```

List AC line segments with electrical parameters:

```bash
pocket-rdf query models/*.xml \
  --dataset \
  --query queries/list_acline_segments.sparql \
  --out output/acline_segments.csv
```

## Validate CGMES Data

Validate the Equipment profile against its SHACL shapes:

```bash
pocket-rdf validate models/*BC_EQ*.xml \
  --dataset \
  --shapes adapted_cgmes_2_4_15_shacl/EquipmentProfile.ttl \
  --out output/eq_validation_report.ttl
```

Validate against all SHACL shapes at once (combine shapes files):

```bash
pocket-rdf validate models/*.xml \
  --dataset \
  --shapes adapted_cgmes_2_4_15_shacl/FileHeaderProfile.ttl \
  --out output/header_validation_report.ttl
```

> **Tip:** For full dataset validation, run the command once per profile shape
> to get targeted reports, or combine all shapes into a single file.
