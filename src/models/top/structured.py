"""
Structured output models for TOP-compliant data using Pydantic.

These models enable AI agents to produce structured, validated data
that seamlessly integrates with the knowledge graph.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

from .base import ConfidenceLevel


class TOPEntityType(str, Enum):
    """Valid TOP entity types."""
    # Government entities
    HOME_RULE_CITY = "HomeRuleCity"
    GENERAL_LAW_CITY = "GeneralLawCity"
    COUNTY = "County"
    DEPARTMENT = "Department"
    DIVISION = "Division"
    SPECIAL_DISTRICT = "SpecialDistrict"
    AUTHORITY = "Authority"
    
    # Political entities
    MAYOR = "Mayor"
    COUNCIL_MEMBER = "CouncilMember"
    CITY_MANAGER = "CityManager"
    COUNTY_JUDGE = "CountyJudge"
    COMMISSIONER = "Commissioner"
    APPOINTED_POSITION = "AppointedPosition"
    ELECTED_POSITION = "ElectedPosition"
    
    # Geographic entities
    COUNCIL_DISTRICT = "CouncilDistrict"
    PRECINCT = "Precinct"
    VOTING_LOCATION = "VotingLocation"
    ADMINISTRATIVE_BOUNDARY = "AdministrativeBoundary"
    
    # Legal documents
    CHARTER = "Charter"
    ORDINANCE = "Ordinance"
    RESOLUTION = "Resolution"
    PROCLAMATION = "Proclamation"
    EXECUTIVE_ORDER = "ExecutiveOrder"
    
    # Basic entities
    PERSON = "Person"


class TOPRelationshipType(str, Enum):
    """Valid TOP relationship types."""
    GOVERNS = "Governs"
    HAS_JURISDICTION_OVER = "HasJurisdictionOver"
    HOLDS_POSITION = "HoldsPosition"
    APPOINTED_BY = "AppointedBy"
    ELECTED_TO = "ElectedTo"
    SUPERSEDED_BY = "SupersededBy"
    PART_OF = "PartOf"
    REPORTS_TO = "ReportsTo"
    SERVES = "Serves"
    AMENDED_BY = "AmendedBy"
    LOCATED_IN = "LocatedIn"
    ADJACENT_TO = "AdjacentTo"


class StructuredEntity(BaseModel):
    """Structured entity for AI agent output."""
    entity_type: TOPEntityType = Field(
        ...,
        description="Type of TOP entity"
    )
    top_id: str = Field(
        ...,
        description="Unique TOP identifier (format: 'fwtx:type:identifier')",
        example="fwtx:mayor:current"
    )
    properties: Dict[str, Any] = Field(
        ...,
        description="Entity-specific properties including entity_name"
    )
    source: str = Field(
        ...,
        description="Source URL or document name"
    )
    confidence: ConfidenceLevel = Field(
        default=ConfidenceLevel.HIGH,
        description="Confidence level in the data accuracy"
    )
    valid_from: Optional[str] = Field(
        None,
        description="ISO date when entity became valid"
    )
    valid_until: Optional[str] = Field(
        None,
        description="ISO date when entity ceased to be valid"
    )
    
    @validator('top_id')
    def validate_top_id_format(cls, v):
        """Ensure TOP ID follows the correct format."""
        if not v.startswith('fwtx:'):
            raise ValueError('TOP ID must start with "fwtx:"')
        parts = v.split(':')
        if len(parts) < 3:
            raise ValueError('TOP ID must have format "fwtx:type:identifier"')
        return v
    
    @validator('properties')
    def ensure_entity_name(cls, v):
        """Ensure entity_name is present in properties."""
        if 'entity_name' not in v:
            raise ValueError('properties must include entity_name')
        return v


class StructuredRelationship(BaseModel):
    """Structured relationship for AI agent output."""
    relationship_type: TOPRelationshipType = Field(
        ...,
        description="Type of TOP relationship"
    )
    source_entity: str = Field(
        ...,
        description="TOP ID of source entity"
    )
    target_entity: str = Field(
        ...,
        description="TOP ID of target entity"
    )
    properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional relationship properties"
    )
    source: str = Field(
        ...,
        description="Source URL or document name"
    )
    confidence: ConfidenceLevel = Field(
        default=ConfidenceLevel.HIGH,
        description="Confidence level in the relationship"
    )
    valid_from: Optional[str] = Field(
        None,
        description="ISO date when relationship became valid"
    )
    valid_until: Optional[str] = Field(
        None,
        description="ISO date when relationship ceased to be valid"
    )


class TOPEpisodeData(BaseModel):
    """
    Structured data for a complete TOP episode.
    This is the primary output format for AI agents.
    """
    entities: List[StructuredEntity] = Field(
        default_factory=list,
        description="List of TOP entities discovered"
    )
    relationships: List[StructuredRelationship] = Field(
        default_factory=list,
        description="List of TOP relationships between entities"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the research/extraction"
    )
    
    def to_episode_content(self) -> str:
        """Convert to JSON string for episode content."""
        return self.model_dump_json(indent=2)
    
    def validate_entity_references(self) -> List[str]:
        """
        Validate that all relationships reference existing entities.
        Returns list of missing entity IDs.
        """
        entity_ids = {entity.top_id for entity in self.entities}
        referenced_ids = set()
        
        for rel in self.relationships:
            referenced_ids.add(rel.source_entity)
            referenced_ids.add(rel.target_entity)
        
        missing_ids = referenced_ids - entity_ids
        return list(missing_ids)
    
    def get_entity_by_id(self, top_id: str) -> Optional[StructuredEntity]:
        """Get entity by TOP ID."""
        for entity in self.entities:
            if entity.top_id == top_id:
                return entity
        return None


# Example structured outputs for specific use cases

class MayorData(BaseModel):
    """Structured data for mayor information."""
    person_name: str = Field(..., description="Full name of the mayor")
    term_start: str = Field(..., description="ISO date when term began")
    term_end: str = Field(..., description="ISO date when term ends")
    election_date: Optional[str] = Field(None, description="Date of election")
    political_party: Optional[str] = Field(None, description="Political party affiliation")
    contact_email: Optional[str] = Field(None, description="Official email")
    contact_phone: Optional[str] = Field(None, description="Office phone number")
    biography_url: Optional[str] = Field(None, description="URL to biography")
    
    def to_top_entity(self, top_id: str = "fwtx:mayor:current") -> StructuredEntity:
        """Convert to TOP entity structure."""
        return StructuredEntity(
            entity_type=TOPEntityType.MAYOR,
            top_id=top_id,
            properties={
                "entity_name": f"Mayor {self.person_name}",
                "person_name": self.person_name,
                "term_start": self.term_start,
                "term_end": self.term_end,
                "election_type": "at-large",
                **self.model_dump(exclude={'person_name', 'term_start', 'term_end'}, exclude_none=True)
            },
            source="AI research",
            confidence=ConfidenceLevel.HIGH,
            valid_from=self.term_start
        )


class DepartmentData(BaseModel):
    """Structured data for department information."""
    department_name: str = Field(..., description="Official department name")
    department_type: str = Field(..., description="Type: utility, public_safety, administrative, etc.")
    director_name: Optional[str] = Field(None, description="Department head name")
    budget_amount: Optional[int] = Field(None, description="Annual budget in dollars")
    employee_count: Optional[int] = Field(None, description="Number of employees")
    website: Optional[str] = Field(None, description="Department website URL")
    services: List[str] = Field(default_factory=list, description="List of services provided")
    
    def to_top_entity(self, top_id: str) -> StructuredEntity:
        """Convert to TOP entity structure."""
        return StructuredEntity(
            entity_type=TOPEntityType.DEPARTMENT,
            top_id=top_id,
            properties={
                "entity_name": self.department_name,
                "department_type": self.department_type,
                "parent_organization": "fwtx:city:fort-worth",
                **self.model_dump(exclude={'department_name'}, exclude_none=True)
            },
            source="AI research",
            confidence=ConfidenceLevel.HIGH,
            valid_from=datetime.now().isoformat()
        )


class CouncilMemberData(BaseModel):
    """Structured data for council member information."""
    person_name: str = Field(..., description="Full name of council member")
    district_number: int = Field(..., description="District number (1-9)")
    term_start: str = Field(..., description="ISO date when term began")
    term_end: str = Field(..., description="ISO date when term ends")
    committee_memberships: List[str] = Field(default_factory=list, description="Committee assignments")
    contact_email: Optional[str] = Field(None, description="Official email")
    contact_phone: Optional[str] = Field(None, description="Office phone")
    
    def to_top_entities(self) -> tuple[StructuredEntity, StructuredEntity, StructuredRelationship]:
        """Convert to TOP entities and relationship."""
        council_member = StructuredEntity(
            entity_type=TOPEntityType.COUNCIL_MEMBER,
            top_id=f"fwtx:councilmember:district-{self.district_number}",
            properties={
                "entity_name": f"Council Member {self.person_name}",
                "person_name": self.person_name,
                "district_number": self.district_number,
                "term_start": self.term_start,
                "term_end": self.term_end,
                "election_type": "single-member-district",
                **self.model_dump(exclude={'person_name', 'district_number', 'term_start', 'term_end'}, exclude_none=True)
            },
            source="AI research",
            confidence=ConfidenceLevel.HIGH,
            valid_from=self.term_start
        )
        
        district = StructuredEntity(
            entity_type=TOPEntityType.COUNCIL_DISTRICT,
            top_id=f"fwtx:district:{self.district_number}",
            properties={
                "entity_name": f"Fort Worth Council District {self.district_number}",
                "district_number": self.district_number
            },
            source="AI research",
            confidence=ConfidenceLevel.HIGH,
            valid_from="2022-01-01"  # Last redistricting
        )
        
        serves_rel = StructuredRelationship(
            relationship_type=TOPRelationshipType.SERVES,
            source_entity=council_member.top_id,
            target_entity=district.top_id,
            properties={"elected": self.term_start},
            source="AI research",
            confidence=ConfidenceLevel.HIGH,
            valid_from=self.term_start
        )
        
        return council_member, district, serves_rel


# Batch research output for multiple entities
class ResearchOutput(BaseModel):
    """Complete research output from AI agent."""
    topic: str = Field(..., description="Research topic")
    timestamp: datetime = Field(default_factory=datetime.now)
    episode_data: TOPEpisodeData = Field(..., description="Structured TOP data")
    raw_findings: Optional[str] = Field(None, description="Raw text findings if needed")
    sources_consulted: List[str] = Field(default_factory=list, description="URLs/sources checked")
    
    def to_episodes(self) -> List[Dict[str, Any]]:
        """Convert to episode format for graphiti ingestion."""
        return [{
            "name": f"{self.topic} - Research Results",
            "content": self.episode_data.to_episode_content(),
            "source": "json",
            "source_description": f"AI researched - {self.topic}",
            "reference_time": self.timestamp
        }]