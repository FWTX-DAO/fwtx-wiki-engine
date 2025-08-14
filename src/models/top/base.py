"""
Base classes and mixins for Texas Ontology Protocol (TOP) entities.

This module provides the foundational classes that implement TOP's core principles:
- Temporal accuracy with bi-temporal modeling
- Hierarchical flexibility
- Geographic precision
- Political neutrality
- Semantic interoperability
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class ConfidenceLevel(str, Enum):
    """Confidence level for facts in the knowledge graph."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"


class TemporalMixin:
    """
    Bi-temporal mixin implementing TOP's temporal accuracy principle.
    
    Tracks both real-world validity and system recording times.
    """
    valid_from: datetime = Field(
        ..., 
        description="When the fact became true in the real world"
    )
    valid_until: Optional[datetime] = Field(
        None, 
        description="When the fact ceased to be true (null if still valid)"
    )
    recorded_at: datetime = Field(
        default_factory=datetime.now,
        description="When the fact was entered into the system"
    )
    superseded_at: Optional[datetime] = Field(
        None,
        description="When the fact was replaced by newer information"
    )
    
    @validator('valid_until')
    def validate_temporal_consistency(cls, v, values):
        """Ensure valid_until is after valid_from if both are set."""
        if v and 'valid_from' in values and v <= values['valid_from']:
            raise ValueError('valid_until must be after valid_from')
        return v
    
    def is_valid_at(self, point_in_time: datetime) -> bool:
        """Check if the entity was valid at a specific point in time."""
        if point_in_time < self.valid_from:
            return False
        if self.valid_until and point_in_time >= self.valid_until:
            return False
        return True
    
    def is_current(self) -> bool:
        """Check if the entity is currently valid."""
        return self.valid_until is None and self.superseded_at is None


class TexasStatePlaneCoords(BaseModel):
    """Texas State Plane coordinate representation."""
    zone: str = Field(..., description="Texas State Plane zone (North, Central, South, etc.)")
    x: float = Field(..., description="Easting coordinate in feet")
    y: float = Field(..., description="Northing coordinate in feet")
    epsg_code: Optional[str] = Field(None, description="EPSG code for the specific zone")
    
    class Config:
        extra = "forbid"  # This ensures additionalProperties: false in JSON Schema


class SpatialMixin:
    """
    Spatial mixin implementing TOP's geographic precision principle.
    
    Uses EPSG:4326 (WGS84) as primary coordinate system with support
    for Texas State Plane coordinates.
    """
    geometry_wkt: Optional[str] = Field(
        None,
        description="Well-Known Text representation of geometry in EPSG:4326"
    )
    texas_state_plane_coords: Optional[TexasStatePlaneCoords] = Field(
        None,
        description="Optional Texas State Plane coordinate representation"
    )
    boundary_source: Optional[str] = Field(
        None,
        description="Legal authority for boundary (ordinance, court order, etc.)"
    )
    
    @validator('geometry_wkt')
    def validate_wkt(cls, v):
        """Basic WKT validation - could be enhanced with actual geometry parsing."""
        if v and not any(v.startswith(t) for t in ['POINT', 'POLYGON', 'LINESTRING', 'MULTIPOLYGON']):
            raise ValueError('Invalid WKT geometry type')
        return v


class SourceAttributionMixin:
    """
    Source attribution mixin for tracking data provenance.
    
    Implements TOP's requirement that every fact must include source attribution.
    """
    source_document: str = Field(
        ...,
        description="Source document or system identifier"
    )
    source_url: Optional[str] = Field(
        None,
        description="URL to source document if available online"
    )
    authority: str = Field(
        ...,
        description="Authority responsible for the information"
    )
    confidence_level: ConfidenceLevel = Field(
        ConfidenceLevel.HIGH,
        description="Confidence level in the accuracy of this information"
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes about data quality or caveats"
    )


class TOPEntity(TemporalMixin, SourceAttributionMixin, BaseModel):
    """
    Base class for all TOP entities.
    
    Combines temporal tracking and source attribution as required by TOP.
    """
    top_id: str = Field(
        ...,
        description="Unique TOP identifier for the entity"
    )
    entity_name: str = Field(
        ...,
        description="Primary name of the entity"
    )
    aliases: Optional[List[str]] = Field(
        None,
        description="Alternative names or variations"
    )
    description: Optional[str] = Field(
        None,
        description="Human-readable description"
    )
    external_ids: Optional[Dict[str, str]] = Field(
        None,
        description="Mappings to external system identifiers"
    )
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        use_enum_values = True
        
    def get_iri(self, base_uri: str = "https://data.texas.gov/") -> str:
        """Generate IRI for the entity following TOP patterns."""
        return f"{base_uri}entity/{self.__class__.__name__.lower()}/{self.top_id}"


class TOPRelationship(TemporalMixin, SourceAttributionMixin, BaseModel):
    """
    Base class for all TOP relationships.
    
    Implements temporal relationships between entities.
    """
    subject_id: str = Field(
        ...,
        description="TOP ID of the subject entity"
    )
    object_id: str = Field(
        ...,
        description="TOP ID of the object entity"
    )
    relationship_type: str = Field(
        ...,
        description="Type of relationship"
    )
    properties: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional relationship properties"
    )
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        use_enum_values = True
        
    def get_triple(self) -> tuple:
        """Return the relationship as a semantic triple."""
        return (self.subject_id, self.relationship_type, self.object_id)