from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# Custom Entity Types

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

entity_types = {
    "Person": Person,
    "Organization": Organization,
    "Project": Project
}

edge_types = {
    "WorksFor": WorksFor,
    "CollaboratesOn": CollaboratesOn,
    "LocatedIn": LocatedIn
}

edge_type_map = {
    ("Person", "Organization"): ["WorksFor"],
    ("Organization", "Organization"): ["CollaboratesOn", "Investment"],
    ("Person", "Person"): ["Partnership"],
    ("Entity", "Entity"): ["Investment"],  # Apply to any entity type
}

async def add_episode(graphiti):
    timestamp = datetime.now()
    await graphiti.add_episode(
        name=f"Fort Worth Episode {timestamp}",
        episode_body=f"Update for fort worth city services {timestamp}",
        source_description="Fort Worth DAO - Munincipal Data Lake",
        reference_time=datetime.now(),
        entity_types=entity_types,
        edge_types=edge_types,
        edge_type_map=edge_type_map
    )
