"""
Relationship models for Texas Ontology Protocol (TOP).

Implements the various relationships between entities in Texas government
including organizational, political, temporal, and spatial relationships.
"""

from typing import Optional, Literal, List, Dict, Any
from datetime import datetime
from pydantic import Field, validator
from .base import TOPRelationship


class Governs(TOPRelationship):
    """
    Relationship indicating a government entity governs a geographic area.
    
    Example: City of Fort Worth governs the area within city limits.
    """
    relationship_type: Literal["governs"] = "governs"
    jurisdiction_type: str = Field(
        ...,
        description="Type of jurisdiction (full, limited, special)"
    )
    services_provided: List[str] = Field(
        default_factory=list,
        description="Services provided to the governed area"
    )
    
    def __init__(self, **data):
        """Ensure subject is government entity and object is geographic."""
        super().__init__(**data)
        # In practice, would validate entity types


class HasJurisdictionOver(TOPRelationship):
    """
    Relationship indicating jurisdictional authority between government entities.
    
    Example: County has jurisdiction over unincorporated areas.
    """
    relationship_type: Literal["has_jurisdiction_over"] = "has_jurisdiction_over"
    jurisdiction_scope: List[str] = Field(
        ...,
        description="Scope of jurisdiction (law enforcement, taxation, etc.)"
    )
    limitations: List[str] = Field(
        default_factory=list,
        description="Limitations on jurisdiction"
    )
    legal_basis: str = Field(
        ...,
        description="Legal basis for jurisdiction"
    )


class HoldsPosition(TOPRelationship):
    """
    Relationship indicating a person holds a political position.
    
    Example: Jane Doe holds position of Mayor.
    """
    relationship_type: Literal["holds_position"] = "holds_position"
    start_date: datetime = Field(
        ...,
        description="Date person assumed the position"
    )
    end_date: Optional[datetime] = Field(
        None,
        description="Date person left the position"
    )
    appointment_type: Literal["elected", "appointed", "hired"] = Field(
        ...,
        description="How the person came to hold the position"
    )
    oath_date: Optional[datetime] = Field(
        None,
        description="Date oath of office was taken"
    )
    term_number: Optional[int] = Field(
        None,
        description="Which term this is (1st, 2nd, etc.)"
    )
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        """Ensure end date is after start date."""
        if v and 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v


class AppointedBy(TOPRelationship):
    """
    Relationship indicating who appointed someone to a position.
    
    Example: City Manager appointed by City Council.
    """
    relationship_type: Literal["appointed_by"] = "appointed_by"
    appointment_date: datetime = Field(
        ...,
        description="Date of appointment"
    )
    confirmation_required: bool = Field(
        False,
        description="Whether appointment required confirmation"
    )
    confirmation_date: Optional[datetime] = Field(
        None,
        description="Date appointment was confirmed"
    )
    confirmation_vote: Optional[Dict[str, int]] = Field(
        None,
        description="Confirmation vote tally if applicable"
    )


class ElectedTo(TOPRelationship):
    """
    Relationship indicating election to a position.
    
    Example: John Smith elected to Council Member District 3.
    """
    relationship_type: Literal["elected_to"] = "elected_to"
    election_date: datetime = Field(
        ...,
        description="Date of election"
    )
    vote_total: Optional[int] = Field(
        None,
        description="Total votes received"
    )
    vote_percentage: Optional[float] = Field(
        None,
        description="Percentage of votes received"
    )
    runoff: bool = Field(
        False,
        description="Whether this was a runoff election"
    )
    opponents: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of opponents with vote totals"
    )


class SupersededBy(TOPRelationship):
    """
    Temporal relationship indicating one entity/document supersedes another.
    
    Example: Ordinance 2024-001 superseded by Ordinance 2024-050.
    """
    relationship_type: Literal["superseded_by"] = "superseded_by"
    supersession_date: datetime = Field(
        ...,
        description="Date the supersession took effect"
    )
    supersession_type: Literal["full", "partial"] = Field(
        ...,
        description="Whether supersession is full or partial"
    )
    affected_sections: List[str] = Field(
        default_factory=list,
        description="Sections affected if partial supersession"
    )
    reason: Optional[str] = Field(
        None,
        description="Reason for supersession"
    )


class PartOf(TOPRelationship):
    """
    Hierarchical relationship indicating containment or membership.
    
    Example: Department part of City Government.
    """
    relationship_type: Literal["part_of"] = "part_of"
    hierarchy_type: str = Field(
        ...,
        description="Type of hierarchy (organizational, geographic, etc.)"
    )
    hierarchy_level: Optional[int] = Field(
        None,
        description="Level in the hierarchy"
    )
    direct_relationship: bool = Field(
        True,
        description="Whether this is a direct parent-child relationship"
    )


class ReportsTo(TOPRelationship):
    """
    Organizational relationship indicating reporting structure.
    
    Example: Police Chief reports to City Manager.
    """
    relationship_type: Literal["reports_to"] = "reports_to"
    reporting_type: Literal["direct", "dotted_line", "functional"] = Field(
        "direct",
        description="Type of reporting relationship"
    )
    frequency: Optional[str] = Field(
        None,
        description="Frequency of reporting (daily, weekly, as needed)"
    )
    report_types: List[str] = Field(
        default_factory=list,
        description="Types of reports provided"
    )


class CollaboratesWith(TOPRelationship):
    """
    Relationship indicating collaboration between entities.
    
    Example: City collaborates with County on emergency services.
    """
    relationship_type: Literal["collaborates_with"] = "collaborates_with"
    collaboration_type: str = Field(
        ...,
        description="Type of collaboration"
    )
    agreement_document_id: Optional[str] = Field(
        None,
        description="TOP ID of agreement document if formal"
    )
    cost_sharing: Optional[Dict[str, float]] = Field(
        None,
        description="Cost sharing arrangement if applicable"
    )
    lead_entity: Optional[str] = Field(
        None,
        description="TOP ID of lead entity if applicable"
    )


class Serves(TOPRelationship):
    """
    Relationship indicating service provision.
    
    Example: Water District serves specific neighborhoods.
    """
    relationship_type: Literal["serves"] = "serves"
    service_type: str = Field(
        ...,
        description="Type of service provided"
    )
    service_area_percentage: Optional[float] = Field(
        None,
        description="Percentage of area served"
    )
    service_population: Optional[int] = Field(
        None,
        description="Population served"
    )
    service_level: Optional[str] = Field(
        None,
        description="Level of service provided"
    )


class LocatedIn(TOPRelationship):
    """
    Spatial relationship indicating location within a boundary.
    
    Example: City Hall located in Downtown District.
    """
    relationship_type: Literal["located_in"] = "located_in"
    location_type: Literal["primary", "secondary", "temporary"] = Field(
        "primary",
        description="Type of location"
    )
    address: Optional[str] = Field(
        None,
        description="Street address if applicable"
    )
    coordinates: Optional[Dict[str, float]] = Field(
        None,
        description="Geographic coordinates (lat, lon)"
    )
    
    @validator('coordinates')
    def validate_coordinates(cls, v):
        """Validate coordinate structure and Texas bounds."""
        if v:
            if 'lat' not in v or 'lon' not in v:
                raise ValueError('Coordinates must include lat and lon')
            # Texas approximate bounds
            if not (25.0 < v['lat'] < 37.0 and -107.0 < v['lon'] < -93.0):
                raise ValueError('Coordinates appear to be outside Texas')
        return v


class AdjacentTo(TOPRelationship):
    """
    Spatial relationship indicating adjacency.
    
    Example: District 1 adjacent to District 2.
    """
    relationship_type: Literal["adjacent_to"] = "adjacent_to"
    boundary_type: str = Field(
        ...,
        description="Type of shared boundary"
    )
    boundary_length_miles: Optional[float] = Field(
        None,
        description="Length of shared boundary in miles"
    )
    crossing_points: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Notable crossing points (bridges, roads, etc.)"
    )


class AmendedBy(TOPRelationship):
    """
    Legal relationship for document amendments.
    
    Example: Charter amended by Proposition A.
    """
    relationship_type: Literal["amended_by"] = "amended_by"
    amendment_date: datetime = Field(
        ...,
        description="Date amendment took effect"
    )
    amendment_type: Literal["addition", "deletion", "modification"] = Field(
        ...,
        description="Type of amendment"
    )
    affected_sections: List[str] = Field(
        ...,
        description="Sections affected by amendment"
    )
    approval_method: str = Field(
        ...,
        description="How amendment was approved (council vote, referendum, etc.)"
    )


class EnforcedBy(TOPRelationship):
    """
    Relationship indicating enforcement responsibility.
    
    Example: Ordinance enforced by Code Compliance Department.
    """
    relationship_type: Literal["enforced_by"] = "enforced_by"
    enforcement_type: str = Field(
        ...,
        description="Type of enforcement (criminal, civil, administrative)"
    )
    enforcement_powers: List[str] = Field(
        default_factory=list,
        description="Specific enforcement powers granted"
    )
    penalty_authority: Optional[str] = Field(
        None,
        description="Authority to impose penalties"
    )