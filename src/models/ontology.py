from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any, Type

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
    ReportsTo
)

# Legacy Entity Types (for backward compatibility)

class Person(BaseModel):
    """Represents an individual person in the knowledge graph."""
    full_name: Optional[str] = Field(None, description="Full name of the person")
    birth_date: Optional[datetime] = Field(None, description="Date of birth")
    email: Optional[str] = Field(None, description="Contact email address")
    phone: Optional[str] = Field(None, description="Contact phone number")
    address: Optional[str] = Field(None, description="Physical address of the person")
    skills: Optional[str] = Field(None, description="Skills or expertise of the person")
    updated_at: Optional[datetime] = Field(None, description="Date the person was last updated")

class Organization(BaseModel):
    """Represents an organization or company in the knowledge graph."""
    full_name: Optional[str] = Field(None, description="Name of the organization")
    founded_date: Optional[datetime] = Field(None, description="Date the organization was founded")
    location: Optional[str] = Field(None, description="Primary location or headquarters")
    website: Optional[str] = Field(None, description="Official website URL")
    capabilities: Optional[str] = Field(None, description="Capabilities or services offered by the organization")
    size: Optional[int] = Field(None, description="Size of the organization")
    updated_at: Optional[datetime] = Field(None, description="Date the organization was last updated")
    

class Project(BaseModel):
    """Represents a project or initiative in the knowledge graph."""
    title: Optional[str] = Field(None, description="Title of the project")
    start_date: Optional[datetime] = Field(None, description="Project start date")
    end_date: Optional[datetime] = Field(None, description="Project end date, if completed")
    description: Optional[str] = Field(None, description="Brief description of the project")
    intent: Optional[str] = Field(None, description="Intent or goal of the project")
    updated_at: Optional[datetime] = Field(None, description="Date the project was last updated")


# Custom Edge Types

class WorksFor(BaseModel):
    """Relationship indicating a person works for an organization."""
    role: Optional[str] = Field(None, description="Role or job title of the person in the organization")
    start_date: Optional[datetime] = Field(None, description="Date the person started working for the organization")
    created_at: Optional[datetime] = Field(None, description="Date the relationship was created")
    updated_at: Optional[datetime] = Field(None, description="Date the relationship was last updated")

class CollaboratesOn(BaseModel):
    """Relationship indicating entities collaborate on a project."""
    contribution: Optional[str] = Field(None, description="Nature of the collaboration or contribution")
    start_date: Optional[datetime] = Field(None, description="Start date of the collaboration")
    created_at: Optional[datetime] = Field(None, description="Date the relationship was created")
    updated_at: Optional[datetime] = Field(None, description="Date the relationship was last updated")

class LocatedIn(BaseModel):
    """Relationship indicating an entity is located in a specific place."""
    address: Optional[str] = Field(None, description="Physical address of the location")
    since: Optional[datetime] = Field(None, description="Date the entity became located there")
    created_at: Optional[datetime] = Field(None, description="Date the relationship was created")
    updated_at: Optional[datetime] = Field(None, description="Date the relationship was last updated")

# Combined entity types (Legacy + TOP)
entity_types: Dict[str, Type[BaseModel]] = {
    # Legacy entities
    "Person": Person,
    "Organization": Organization,
    "Project": Project,
    
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

# Combined edge types (Legacy + TOP)
edge_types: Dict[str, Type[BaseModel]] = {
    # Legacy relationships
    "WorksFor": WorksFor,
    "CollaboratesOn": CollaboratesOn,
    "LocatedIn": LocatedIn,
    
    # TOP Relationships
    "Governs": Governs,
    "HasJurisdictionOver": HasJurisdictionOver,
    "HoldsPosition": HoldsPosition,
    "AppointedBy": AppointedBy,
    "ElectedTo": ElectedTo,
    "SupersededBy": SupersededBy,
    "PartOf": PartOf,
    "ReportsTo": ReportsTo,
}

# Extended edge type map including TOP relationships
edge_type_map = {
    # Legacy mappings
    ("Person", "Organization"): ["WorksFor"],
    ("Organization", "Organization"): ["CollaboratesOn", "Investment"],
    ("Person", "Person"): ["Partnership"],
    ("Entity", "Entity"): ["Investment"],  # Apply to any entity type
    
    # TOP Government relationships
    ("GovernmentEntity", "AdministrativeBoundary"): ["Governs"],
    ("GovernmentEntity", "GovernmentEntity"): ["HasJurisdictionOver", "PartOf"],
    ("Department", "GovernmentEntity"): ["PartOf"],
    ("Division", "Department"): ["PartOf"],
    
    # TOP Political relationships
    ("Person", "ElectedPosition"): ["HoldsPosition", "ElectedTo"],
    ("Person", "AppointedPosition"): ["HoldsPosition", "AppointedBy"],
    ("Person", "Person"): ["AppointedBy", "ReportsTo"],
    
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
        name=name,
        source_document=source_document,
        authority=authority,
        valid_from=valid_from,
        recorded_at=datetime.now(),
        **kwargs
    )
