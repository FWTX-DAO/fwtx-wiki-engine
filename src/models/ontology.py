from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Type

# Import Texas Ontology Protocol (TOP) entities and relationships
from .top import (
    # Base classes
    TOPEntity,
    TOPRelationship,
    TemporalMixin,
    SpatialMixin,
    SourceAttributionMixin,
    
    # Government entities
    GovernmentEntity,
    Municipality,
    HomeRuleCity,
    GeneralLawCity,
    County,
    Department,
    Division,
    SpecialDistrict,
    Authority,
    
    # Political entities
    ElectedPosition,
    AppointedPosition,
    Mayor,
    CouncilMember,
    CityManager,
    CountyJudge,
    Commissioner,
    Term,
    ElectionCycle,
    
    # Geographic entities
    AdministrativeBoundary,
    CouncilDistrict,
    Precinct,
    VotingLocation,
    TexasAddress,
    
    # Legal documents
    LegalDocument,
    Ordinance,
    Resolution,
    Charter,
    Proclamation,
    ExecutiveOrder,
    
    # Relationships
    Governs,
    HasJurisdictionOver,
    HoldsPosition,
    AppointedBy,
    ElectedTo,
    SupersededBy,
    PartOf,
    ReportsTo,
    Serves
)

# No legacy entities - using only TOP entities

# Create a simple Person entity for TOP
class Person(BaseModel):
    """Simple person entity for holding positions."""
    entity_name: str
    entity_type: str = "person"

# TOP entity types only
entity_types: Dict[str, Type[BaseModel]] = {
    # Basic entities
    "Person": Person,
    
    # TOP Government entities
    "GovernmentEntity": GovernmentEntity,
    "Municipality": Municipality,
    "HomeRuleCity": HomeRuleCity,
    "GeneralLawCity": GeneralLawCity,
    "County": County,
    "Department": Department,
    "Division": Division,
    "SpecialDistrict": SpecialDistrict,
    "Authority": Authority,
    
    # TOP Political entities
    "ElectedPosition": ElectedPosition,
    "AppointedPosition": AppointedPosition,
    "Mayor": Mayor,
    "CouncilMember": CouncilMember,
    "CityManager": CityManager,
    "CountyJudge": CountyJudge,
    "Commissioner": Commissioner,
    "Term": Term,
    "ElectionCycle": ElectionCycle,
    
    # TOP Geographic entities
    "AdministrativeBoundary": AdministrativeBoundary,
    "CouncilDistrict": CouncilDistrict,
    "Precinct": Precinct,
    "VotingLocation": VotingLocation,
    "TexasAddress": TexasAddress,
    
    # TOP Legal documents
    "LegalDocument": LegalDocument,
    "Ordinance": Ordinance,
    "Resolution": Resolution,
    "Charter": Charter,
    "Proclamation": Proclamation,
    "ExecutiveOrder": ExecutiveOrder,
}

# TOP edge types only
edge_types: Dict[str, Type[BaseModel]] = {
    # TOP Relationships
    "Governs": Governs,
    "HasJurisdictionOver": HasJurisdictionOver,
    "HoldsPosition": HoldsPosition,
    "AppointedBy": AppointedBy,
    "ElectedTo": ElectedTo,
    "SupersededBy": SupersededBy,
    "PartOf": PartOf,
    "ReportsTo": ReportsTo,
    "Serves": Serves,
}

# TOP edge type map
edge_type_map = {
    # TOP Government relationships
    ("GovernmentEntity", "AdministrativeBoundary"): ["Governs"],
    ("GovernmentEntity", "GovernmentEntity"): ["HasJurisdictionOver", "PartOf"],
    ("Department", "GovernmentEntity"): ["PartOf"],
    ("Division", "Department"): ["PartOf"],
    
    # TOP Political relationships
    ("Person", "ElectedPosition"): ["HoldsPosition", "ElectedTo"],
    ("Person", "AppointedPosition"): ["HoldsPosition", "AppointedBy"],
    ("Person", "Person"): ["AppointedBy", "ReportsTo"],
    ("CouncilMember", "CouncilDistrict"): ["Serves"],
    ("Mayor", "HomeRuleCity"): ["Governs"],
    
    # TOP Legal relationships
    ("LegalDocument", "LegalDocument"): ["SupersededBy", "AmendedBy"],
    ("Ordinance", "Ordinance"): ["SupersededBy"],
    ("Resolution", "Resolution"): ["SupersededBy"],
    
    # TOP Geographic relationships
    ("GovernmentEntity", "TexasAddress"): ["LocatedIn"],
    ("VotingLocation", "Precinct"): ["LocatedIn"],
    ("AdministrativeBoundary", "AdministrativeBoundary"): ["AdjacentTo"],
}

async def add_episode(graphiti, episode_type: str = "general"):
    """
    Add a new episode to the knowledge graph.
    
    Args:
        graphiti: The graphiti instance
        episode_type: Type of episode - 'general', 'government', 'election', etc.
    """
    timestamp = datetime.now()
    
    episode_descriptions = {
        "general": "General update for Fort Worth city services",
        "government": "Government structure and personnel update",
        "election": "Election and political position update",
        "legal": "Legal document and ordinance update",
        "geographic": "Geographic boundary and location update"
    }
    
    episode_body = episode_descriptions.get(
        episode_type, 
        "Update for Fort Worth city services"
    )
    
    await graphiti.add_episode(
        name=f"Fort Worth Episode {timestamp} - {episode_type.title()}",
        episode_body=f"{episode_body} - {timestamp}",
        source_description="Fort Worth DAO - Municipal Data Lake (TOP v0.0.1)",
        reference_time=datetime.now(),
        entity_types=entity_types,
        edge_types=edge_types,
        edge_type_map=edge_type_map
    )
    
# Helper function to create TOP-compliant entities
def create_top_entity(
    entity_class: Type[TOPEntity],
    top_id: str,
    name: str,
    source_document: str,
    authority: str,
    valid_from: datetime,
    **kwargs
) -> TOPEntity:
    """
    Create a TOP-compliant entity with required temporal and source attribution.
    
    Args:
        entity_class: The TOP entity class to instantiate
        top_id: Unique TOP identifier
        name: Entity name
        source_document: Source document identifier
        authority: Authority responsible for the information
        valid_from: When the entity became valid
        **kwargs: Additional entity-specific fields
    
    Returns:
        Instantiated TOP entity
    """
    return entity_class(
        top_id=top_id,
        entity_name=name,
        source_document=source_document,
        authority=authority,
        valid_from=valid_from,
        recorded_at=datetime.now(),
        **kwargs
    )
