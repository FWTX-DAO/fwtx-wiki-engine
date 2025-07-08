# Texas Ontology Protocol (TOP) v0.0.1

## Abstract

The Texas Ontology Protocol (TOP) provides a standardized framework for modeling Texas municipal and county government structures in knowledge graphs. TOP enables consistent representation of governmental entities, relationships, and temporal changes across Texas jurisdictions, facilitating data interoperability and intelligent query capabilities.

## Table of Contents

1. [Introduction](#introduction)
2. [Core Principles](#core-principles)
3. [Namespace and Prefixes](#namespace-and-prefixes)
4. [Entity Types](#entity-types)
5. [Relationships](#relationships)
6. [Temporal Modeling](#temporal-modeling)
7. [Spatial Modeling](#spatial-modeling)
8. [Implementation Guidelines](#implementation-guidelines)
9. [Query Patterns](#query-patterns)
10. [Conformance](#conformance)

## Introduction

Texas has unique governmental structures including home-rule cities, council-manager forms of government, and specific requirements under the Texas Local Government Code. TOP provides a semantic framework that captures these structures while maintaining compatibility with international standards.

### Scope

TOP covers:
- Municipal government structures (cities, towns)
- County government structures
- Special districts and authorities
- Political positions and office holders
- Legislative documents (ordinances, resolutions)
- Electoral processes and boundaries
- Inter-governmental relationships

### Design Goals

1. **Accuracy**: Precisely model Texas-specific governmental structures
2. **Interoperability**: Align with W3C and other international standards
3. **Temporality**: Track changes over time with bi-temporal modeling
4. **Extensibility**: Allow jurisdictions to add local extensions
5. **Queryability**: Support complex temporal and spatial queries

## Core Principles

### Principle 1: Temporal Accuracy
Every fact in a TOP-compliant knowledge graph MUST have temporal validity metadata:
- `valid_from`: When the fact became true in the real world
- `valid_until`: When the fact ceased to be true (null if still valid)
- `recorded_at`: When the fact was entered into the system
- `superseded_at`: When the fact was replaced by newer information

### Principle 2: Hierarchical Flexibility
TOP models accommodate Texas's varied governmental structures:
- Home-rule cities with custom charters
- General law cities following state templates
- Counties with varying urbanization levels
- Overlapping jurisdictions and authorities

### Principle 3: Geographic Precision
All spatial data MUST:
- Use EPSG:4326 (WGS84) as the primary coordinate system
- Support Texas State Plane coordinate systems for local use
- Maintain historical boundary data through temporal validity
- Link geographic changes to legal authorities (ordinances, court orders)

### Principle 4: Political Neutrality
TOP implementations MUST:
- Represent factual relationships without bias
- Track all political affiliations equally
- Maintain complete audit trails
- Separate opinions from facts in annotations

### Principle 5: Semantic Interoperability
TOP aligns with established ontologies:
- W3C Organization Ontology (ORG) for hierarchies
- FOAF for people and organizations
- Dublin Core for documents
- GeoSPARQL for spatial data
- OWL-Time for temporal relationships

## Namespace and Prefixes

```turtle
@prefix top: <https://ontology.texas.gov/top/v1#> .
@prefix topgov: <https://ontology.texas.gov/top/v1/government#> .
@prefix toppol: <https://ontology.texas.gov/top/v1/political#> .
@prefix topgeo: <https://ontology.texas.gov/top/v1/geographic#> .
@prefix toplegal: <https://ontology.texas.gov/top/v1/legal#> .

# Standard prefixes used by TOP
@prefix org: <http://www.w3.org/ns/org#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix time: <http://www.w3.org/2006/time#> .
@prefix geo: <http://www.opengis.net/ont/geosparql#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
```

## Entity Types

### Government Organizations

```turtle
# Base government entity
topgov:GovernmentEntity rdfs:subClassOf org:Organization ;
    rdfs:label "Government Entity"@en ;
    rdfs:comment "A governmental organization in Texas"@en .

# Municipal entities
topgov:Municipality rdfs:subClassOf topgov:GovernmentEntity ;
    rdfs:label "Municipality"@en .

topgov:HomeRuleCity rdfs:subClassOf topgov:Municipality ;
    rdfs:label "Home Rule City"@en ;
    rdfs:comment "City with population >5,000 and adopted charter"@en ;
    top:requiredProperties ( topgov:charter topgov:population ) .

topgov:GeneralLawCity rdfs:subClassOf topgov:Municipality ;
    rdfs:label "General Law City"@en ;
    rdfs:comment "City operating under state law without custom charter"@en .

# County entities
topgov:County rdfs:subClassOf topgov:GovernmentEntity ;
    rdfs:label "County"@en ;
    rdfs:comment "One of 254 Texas counties"@en .

# Departments and divisions
topgov:Department rdfs:subClassOf org:OrganizationalUnit ;
    rdfs:label "Department"@en .

topgov:Division rdfs:subClassOf org:OrganizationalUnit ;
    rdfs:label "Division"@en .
```

### Political Positions and Roles

```turtle
# Positions
toppol:ElectedPosition rdfs:subClassOf org:Post ;
    rdfs:label "Elected Position"@en .

toppol:AppointedPosition rdfs:subClassOf org:Post ;
    rdfs:label "Appointed Position"@en .

# Specific positions
toppol:Mayor rdfs:subClassOf toppol:ElectedPosition ;
    rdfs:label "Mayor"@en .

toppol:CouncilMember rdfs:subClassOf toppol:ElectedPosition ;
    rdfs:label "Council Member"@en .

toppol:CityManager rdfs:subClassOf toppol:AppointedPosition ;
    rdfs:label "City Manager"@en .

toppol:CountyJudge rdfs:subClassOf toppol:ElectedPosition ;
    rdfs:label "County Judge"@en ;
    rdfs:comment "Chief executive of Texas county"@en .

# Terms of office
toppol:Term rdfs:subClassOf time:ProperInterval ;
    rdfs:label "Term of Office"@en ;
    top:requiredProperties ( time:hasBeginning time:hasEnd toppol:position ) .
```

### Geographic Entities

```turtle
topgeo:AdministrativeBoundary rdfs:subClassOf geo:Feature ;
    rdfs:label "Administrative Boundary"@en .

topgeo:CouncilDistrict rdfs:subClassOf topgeo:AdministrativeBoundary ;
    rdfs:label "Council District"@en .

topgeo:Precinct rdfs:subClassOf topgeo:AdministrativeBoundary ;
    rdfs:label "Precinct"@en .

topgeo:VotingLocation rdfs:subClassOf geo:Feature ;
    rdfs:label "Voting Location"@en .
```

### Legal Documents

```turtle
toplegal:LegalDocument rdfs:subClassOf foaf:Document ;
    rdfs:label "Legal Document"@en .

toplegal:Ordinance rdfs:subClassOf toplegal:LegalDocument ;
    rdfs:label "Ordinance"@en ;
    top:requiredProperties ( dct:identifier dct:title dct:date ) .

toplegal:Resolution rdfs:subClassOf toplegal:LegalDocument ;
    rdfs:label "Resolution"@en .

toplegal:Charter rdfs:subClassOf toplegal:LegalDocument ;
    rdfs:label "City Charter"@en .
```

## Relationships

### Organizational Relationships

```turtle
# Hierarchical relationships
topgov:governs rdfs:subPropertyOf org:subOrganizationOf ;
    rdfs:label "governs"@en ;
    rdfs:domain topgov:GovernmentEntity ;
    rdfs:range geo:Feature .

topgov:hasJurisdictionOver rdfs:label "has jurisdiction over"@en ;
    rdfs:domain topgov:GovernmentEntity ;
    rdfs:range topgov:GovernmentEntity .

# Position relationships
toppol:holdsPosition rdfs:subPropertyOf org:holds ;
    rdfs:label "holds position"@en ;
    rdfs:domain foaf:Person ;
    rdfs:range org:Post .

toppol:appointedBy rdfs:label "appointed by"@en ;
    rdfs:domain foaf:Person ;
    rdfs:range foaf:Person .

toppol:electedTo rdfs:label "elected to"@en ;
    rdfs:domain foaf:Person ;
    rdfs:range toppol:ElectedPosition .
```

### Temporal Relationships

```turtle
top:validFrom rdfs:label "valid from"@en ;
    rdfs:range xsd:dateTime ;
    rdfs:comment "When fact became true in reality"@en .

top:validUntil rdfs:label "valid until"@en ;
    rdfs:range xsd:dateTime ;
    rdfs:comment "When fact ceased to be true"@en .

top:recordedAt rdfs:label "recorded at"@en ;
    rdfs:range xsd:dateTime ;
    rdfs:comment "When fact was entered in system"@en .

top:supersededBy rdfs:label "superseded by"@en ;
    rdfs:comment "Points to newer version of fact"@en .
```

## Temporal Modeling

### Bi-Temporal Pattern

Every fact assertion follows this pattern:

```turtle
# Example: Mayor appointment
_:fact1 a top:Fact ;
    top:subject :JaneDoe ;
    top:predicate toppol:holdsPosition ;
    top:object :MayorPosition ;
    top:validFrom "2022-06-15T00:00:00"^^xsd:dateTime ;
    top:validUntil "2024-06-15T00:00:00"^^xsd:dateTime ;
    top:recordedAt "2022-05-20T14:30:00"^^xsd:dateTime ;
    top:source :Ordinance2022-123 .
```

### Election Cycles

```turtle
# Texas uniform election dates
top:UniformElectionDate rdfs:subClassOf time:Instant ;
    rdfs:label "Uniform Election Date"@en .

top:MayElection rdfs:subClassOf top:UniformElectionDate ;
    rdfs:comment "First Saturday in May (odd years)"@en .

top:NovemberElection rdfs:subClassOf top:UniformElectionDate ;
    rdfs:comment "First Tuesday after first Monday in November"@en .
```

## Spatial Modeling

### Boundary Representation

```turtle
# Council district with temporal boundaries
:District3 a topgeo:CouncilDistrict ;
    rdfs:label "District 3"@en ;
    geo:hasGeometry :District3Geometry2023 ;
    top:validFrom "2023-01-01T00:00:00"^^xsd:dateTime .

:District3Geometry2023 a geo:Geometry ;
    geo:asWKT "POLYGON((...))"^^geo:wktLiteral ;
    top:validFrom "2023-01-01T00:00:00"^^xsd:dateTime ;
    top:source :RedistrictingOrdinance2022 .
```

### Address Resolution

```turtle
top:hasAddress rdfs:label "has address"@en ;
    rdfs:domain geo:Feature ;
    rdfs:range top:TexasAddress .

top:TexasAddress rdfs:subClassOf schema:PostalAddress ;
    top:requiredProperties ( 
        schema:streetAddress 
        schema:addressLocality 
        schema:addressRegion 
        schema:postalCode 
    ) .
```

## Implementation Guidelines

### 1. Entity Resolution

Implementations MUST:
- Generate unique IRIs for entities using consistent patterns
- Implement similarity matching for deduplication
- Maintain alias relationships for name variations
- Track entity mergers and splits temporally

### 2. Data Validation

All data MUST be validated against:
- Required properties for each entity type
- Temporal consistency rules
- Spatial boundary validity
- Legal citation formats

### 3. Source Attribution

Every fact MUST include:
- Source document or system
- Timestamp of assertion
- Authority for the information
- Confidence level (if applicable)

### 4. API Design

TOP-compliant APIs SHOULD:
- Support temporal queries with `asOf` parameters
- Enable spatial queries with GeoSPARQL
- Provide both current and historical views
- Return provenance metadata

## Query Patterns

### Point-in-Time Queries

```sparql
# Who was mayor on a specific date?
SELECT ?person ?name WHERE {
    ?fact a top:Fact ;
          top:subject ?person ;
          top:predicate toppol:holdsPosition ;
          top:object :MayorPosition ;
          top:validFrom ?from ;
          top:validUntil ?until .
    ?person foaf:name ?name .
    FILTER(?from <= "2023-07-01"^^xsd:dateTime)
    FILTER(?until > "2023-07-01"^^xsd:dateTime || !bound(?until))
}
```

### Spatial Queries

```sparql
# Which council district contains an address?
SELECT ?district WHERE {
    ?district a topgeo:CouncilDistrict ;
              geo:hasGeometry ?geometry .
    ?geometry geo:contains ?point .
    ?point geo:asWKT "POINT(-97.3208 32.7357)"^^geo:wktLiteral .
}
```

### Relationship Traversal

```sparql
# Find all committee memberships for a person
SELECT ?committee ?role ?from ?until WHERE {
    ?membership a top:Fact ;
                top:subject :JohnSmith ;
                top:predicate org:memberOf ;
                top:object ?committee ;
                top:validFrom ?from ;
                top:validUntil ?until .
    OPTIONAL { ?membership org:role ?role }
}
```

## Conformance

### Levels of Conformance

1. **TOP-Basic**: Implements core entity types and relationships
2. **TOP-Temporal**: Adds full bi-temporal support
3. **TOP-Spatial**: Includes GeoSPARQL compliance
4. **TOP-Complete**: Full implementation of all features

### Validation

Conformance can be tested using:
- SHACL shapes provided in the TOP repository
- Reference test suite with example data
- Automated validation service at https://validate.texas.gov/top

### Extensions

Jurisdictions may extend TOP by:
- Adding subclasses of TOP classes
- Creating new properties with TOP classes as domain
- Defining local controlled vocabularies
- Documenting extensions in `top-local:` namespace

## References

1. [Texas Local Government Code](https://statutes.capitol.texas.gov/Docs/LG/htm/LG.1.htm)
2. [W3C Organization Ontology](https://www.w3.org/TR/vocab-org/)
3. [GeoSPARQL 1.1](https://www.ogc.org/standards/geosparql)
4. [FOAF Vocabulary](http://xmlns.com/foaf/0.1/)
5. [Dublin Core Terms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/)

## Version History

- v0.0.1 (2024-01): Initial release

## License

This specification is released under Creative Commons Attribution 4.0 International (CC BY 4.0).

## Contact

Texas Ontology Protocol Working Group  
Email: community@fwtx.city
GitHub: https://github.com/FWTX-DAO