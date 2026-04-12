← [Back to main README](../../README.md) · [Simple examples](../simple/) · [Advanced examples](../advanced/)

# CGMES Examples

These examples demonstrate one important use case for pocket-rdf:
**validating and querying CGMES (Common Grid Model Exchange Standard) datasets**
used in the European power system industry.

CGMES datasets consist of multiple RDF/XML files, each representing a distinct
profile (Equipment, Topology, State Variables, etc.). pocket-rdf loads each file
into its own named graph (`--dataset`), enabling profile-aware validation and
querying.

## Prerequisites

### 1. Install pocket-rdf

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
├── adapted_cgmes_2_4_15_shacl/    ← SHACL shapes (included)
├── models/                        ← CGMES XML files (you provide)
│   ├── MiniGridTestConfiguration_BC_DL_v3.0.0.xml
│   ├── MiniGridTestConfiguration_BC_EQ_v3.0.0.xml
│   ├── MiniGridTestConfiguration_BC_SSH_v3.0.0.xml
│   ├── MiniGridTestConfiguration_BC_SV_v3.0.0.xml
│   ├── MiniGridTestConfiguration_BC_TP_v3.0.0.xml
│   ├── MiniGridTestConfiguration_EQ_BD_v3.0.0.xml
│   ├── MiniGridTestConfiguration_TP_BD_v3.0.0.xml
│   └── ...
├── output/                        ← Generated output (git-ignored)
├── queries/                       ← SPARQL queries (included)
└── ...
```

### 3. Navigate to working directory

```
examples/cgmes
```

## Queries

| File | Description |
|------|-------------|
| `queries/list_model_headers.sparql` | List FullModel headers from each profile. |
| `queries/count_triples_per_graph.sparql` | Count triples per named graph (profile). |
| `queries/list_types_per_graph.sparql` | List CIM types and instance counts per profile. |
| `queries/list_substations.sparql` | List all Substations with name and region. |
| `queries/list_acline_segments.sparql` | List ACLineSegments with length and resistance. |
| `queries/rdfs_list_conducting_equipment.sparql` | List all ConductingEquipment instances using the RDFS class hierarchy. |
| `queries/rdfs_discover_properties.sparql` | Discover all properties defined for ACLineSegment in the RDFS. |

## SHACL Shapes

The `adapted_cgmes_2_4_15_shacl/` directory contains SHACL shapes adapted for
CGMES v2.4.15 profiles, originally licensed by ENTSO-E under the Apache License 2.0 (see
`LICENSE.txt` and `NOTICE.txt`).

> **Why adapted shapes?**
> The original SHACL shapes published at
> [entsoe/application-profiles-library](https://github.com/entsoe/application-profiles-library/tree/main/CGMES/PastReleases/v2-4/Enchanced/SHACL)
> are not suitable for validating CGMES CIM/XML test models as-is. They require
> property values to be typed as `xsd:float`, `xsd:boolean`, `xsd:integer`,
> `xsd:decimal`, `xsd:dateTime`, etc., whereas the official CGMES CIM/XML test
> files (and the CGMES specification itself) serialize all datatypes as plain
> string literals. The shapes in this directory have been adapted accordingly.
> The specific modifications applied to each file are documented in the comment
> section at the beginning of each adapted `.ttl` file.

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

## 1. Serialize CGMES Data

Convert the dataset to TriG format (preserving named graphs):

```bash
pocket-rdf serialize models/*.xml \
  --dataset \
  --out output/cgmes_dataset.trig
```

## 2. Query CGMES Data

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

## 3. RDFS-Enhanced Querying

The queries above work on instance data alone. By loading the
[Equipment RDFS](https://github.com/entsoe/application-profiles-library/blob/main/CGMES/PastReleases/v2-4/Original/RDFS/EquipmentProfileCoreOperationShortCircuitRDFSAugmented-v2_4_15-4Sep2020.rdf)
alongside the instance data, SPARQL queries can join instance data with schema
metadata — class descriptions, inheritance hierarchies, and property definitions
— without any code changes.

### Download the RDFS file

Download the Equipment RDFS file from the ENTSO-E application profiles library
and place it in the `rdfs/` directory:

https://github.com/entsoe/application-profiles-library/blob/main/CGMES/PastReleases/v2-4/Original/RDFS/EquipmentProfileCoreOperationShortCircuitRDFSAugmented-v2_4_15-4Sep2020.rdf

Example directory structure after setup:

```
examples/cgmes/
├── adapted_cgmes_2_4_15_shacl/    ← SHACL shapes (included)
├── models/                        ← CGMES XML files (you provide)
├── output/                        ← Generated output (git-ignored)
├── queries/                       ← SPARQL queries (included)
└── rdfs/                          ← Equipment RDFS file (you provide)
    └── EquipmentProfileCoreOperationShortCircuitRDFSAugmented-v2_4_15-4Sep2020.rdf
```

### List all ConductingEquipment instances

Instance data only contains concrete types (`ACLineSegment`, `Breaker`,
`PowerTransformer`, etc.). There is no `rdf:type cim:ConductingEquipment`
triple in the data. By walking `rdfs:subClassOf+` from the RDFS, this query
discovers every class that is a transitive subclass of `ConductingEquipment`
and matches instances of those types:

```bash
pocket-rdf query models/*BC_EQ*.xml rdfs/*.rdf \
  --dataset \
  --query queries/rdfs_list_conducting_equipment.sparql \
  --out output/conducting_equipment.csv
```

### Discover properties defined for a class

Query the RDFS alone (no instance data needed) to list every property defined
for `ACLineSegment`, including data type, multiplicity, and description:

```bash
pocket-rdf query rdfs/*.rdf \
  --dataset \
  --query queries/rdfs_discover_properties.sparql \
  --out output/acline_properties.csv
```

## 4. Validate CGMES Data

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

When a profile references entities defined in another profile (e.g., Equipment
references Equipment Boundary definitions), use `--context` to load the
referenced profile for reference resolution without validating it:

```bash
pocket-rdf validate models/*BC_EQ*.xml \
  --dataset \
  --shapes adapted_cgmes_2_4_15_shacl/EquipmentProfile.ttl \
  --out output/eq_validation_report.ttl \
  --context models/*EQ_BD*.xml
```

> **Note:** Files passed via `--context` are loaded into the dataset so that
> cross-profile references can be resolved, but only the files listed as
> positional arguments are validated against the SHACL shapes.

### Known limitation: `--context` and shared subjects

In CGMES, certain resource URIs (e.g., `ConnectivityNode`, `Terminal`) appear
in multiple profiles. When context files are loaded alongside the data files,
all triples for a shared subject are merged into the same dataset. SHACL
validation then sees properties from both the target profile and the context
profile for that subject.

This means that **closed-shape constraints** (`sh:closed true`) in the target
profile's shapes may flag properties that legitimately belong to the context
profile as violations. For example, when validating a Topology (TP) file with
Equipment (EQ) as context, the TP shapes may report EQ-specific properties
like `ConnectivityNode.ConnectivityNodeContainer` as "not part of the profile",
even though those properties only exist in the EQ file.

This is a fundamental consequence of how SHACL operates on a merged RDF graph
— it has no concept of which file a triple originated from.

If the closed-shape constraints use `sh:severity sh:Info` (or `sh:Warning`),
you can suppress these false violations with the `--allow-infos` (or
`--allow-warnings`) flag:

```bash
pocket-rdf validate models/*BC_TP*.xml \
  --dataset \
  --shapes adapted_cgmes_2_4_15_shacl/TopologyProfile.ttl \
  --out output/tp_validation_report.ttl \
  --context models/*BC_EQ*.xml \
  --allow-infos
```

### Best practice: split shapes by concern

To work around this limitation, consider splitting your SHACL shapes into two
categories:

1. **Reference-checking shapes** — validate that cross-profile references
   resolve correctly (e.g., `sh:class`, `sh:nodeKind`, cardinality
   constraints). These shapes benefit from `--context` because additional
   profiles provide the referenced instances.

2. **Closed-property shapes** — validate that a resource only contains
   properties allowed by its profile (`sh:closed true`, allowed-properties
   constraints). These shapes should be run **without** `--context`, because
   context files introduce properties from other profiles that trigger false
   violations.

By running these two shape categories in separate validation passes, you get
accurate results for both cross-profile reference resolution and
profile-specific property constraints:

```bash
# Pass 1: Check cross-profile references (with context)
pocket-rdf validate models/*BC_TP*.xml \
  --dataset \
  --shapes shapes/tp_reference_shapes.ttl \
  --out output/tp_references_report.ttl \
  --context models/*BC_EQ*.xml

# Pass 2: Check allowed properties (without context)
pocket-rdf validate models/*BC_TP*.xml \
  --dataset \
  --shapes shapes/tp_closed_shapes.ttl \
  --out output/tp_properties_report.ttl
```
