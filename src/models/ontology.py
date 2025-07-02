from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# Custom Entity Types

class Person(BaseModel):
    """Represents an individual person in the knowledge graph."""
    name: Optional[str] = Field(None, description="Full name of the person")
    birth_date: Optional[datetime] = Field(None, description="Date of birth")
    email: Optional[str] = Field(None, description="Contact email address")
    phone: Optional[str] = Field(None, description="Contact phone number")

class Organization(BaseModel):
    """Represents an organization or company in the knowledge graph."""
    name: Optional[str] = Field(None, description="Name of the organization")
    founded_date: Optional[datetime] = Field(None, description="Date the organization was founded")
    location: Optional[str] = Field(None, description="Primary location or headquarters")
    website: Optional[str] = Field(None, description="Official website URL")

class Project(BaseModel):
    """Represents a project or initiative in the knowledge graph."""
    title: Optional[str] = Field(None, description="Title of the project")
    start_date: Optional[datetime] = Field(None, description="Project start date")
    end_date: Optional[datetime] = Field(None, description="Project end date, if completed")
    description: Optional[str] = Field(None, description="Brief description of the project")

# Custom Edge Types

class WorksFor(BaseModel):
    """Relationship indicating a person works for an organization."""
    role: Optional[str] = Field(None, description="Role or job title of the person in the organization")
    start_date: Optional[datetime] = Field(None, description="Date the person started working for the organization")

class CollaboratesOn(BaseModel):
    """Relationship indicating entities collaborate on a project."""
    contribution: Optional[str] = Field(None, description="Nature of the collaboration or contribution")
    start_date: Optional[datetime] = Field(None, description="Start date of the collaboration")

class LocatedIn(BaseModel):
    """Relationship indicating an entity is located in a specific place."""
    address: Optional[str] = Field(None, description="Physical address of the location")
    since: Optional[datetime] = Field(None, description="Date the entity became located there")