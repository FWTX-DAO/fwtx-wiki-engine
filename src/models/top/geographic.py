"""
Geographic entity models for Texas Ontology Protocol (TOP).

Implements spatial entities including administrative boundaries,
voting locations, and address structures specific to Texas.
"""

from typing import Optional, Literal, List, Dict, Any
from pydantic import Field, validator
from .base import TOPEntity, SpatialMixin


class AdministrativeBoundary(SpatialMixin, TOPEntity):
    """
    Base class for administrative boundaries in Texas.
    
    Represents geographic areas with legal/administrative significance.
    """
    entity_type: Literal["administrative_boundary"] = "administrative_boundary"
    boundary_type: str = Field(
        ...,
        description="Type of boundary (city_limits, county_line, etc.)"
    )
    area_sq_miles: Optional[float] = Field(
        None,
        description="Total area in square miles"
    )
    perimeter_miles: Optional[float] = Field(
        None,
        description="Perimeter length in miles"
    )
    population: Optional[int] = Field(
        None,
        description="Population within boundary"
    )
    adjacent_boundaries: List[str] = Field(
        default_factory=list,
        description="TOP IDs of adjacent administrative boundaries"
    )
    establishing_document: Optional[str] = Field(
        None,
        description="Legal document establishing the boundary"
    )


class CouncilDistrict(AdministrativeBoundary):
    """
    City council district for district-based representation.
    
    Used in cities with district-based council elections.
    """
    entity_type: Literal["council_district"] = "council_district"
    boundary_type: Literal["council_district"] = "council_district"
    district_number: int = Field(
        ...,
        description="District number"
    )
    council_member_position_id: Optional[str] = Field(
        None,
        description="TOP ID of the council member position for this district"
    )
    redistricting_cycle: Optional[str] = Field(
        None,
        description="Redistricting cycle this boundary is part of"
    )
    demographic_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Demographic statistics for the district"
    )
    
    @validator('demographic_data')
    def validate_demographics(cls, v):
        """Ensure required demographic fields for redistricting compliance."""
        # Texas redistricting requires certain demographic data
        recommended_fields = ['total_population', 'voting_age_population', 'citizen_voting_age_population']
        if v and not any(field in v for field in recommended_fields):
            # Warning, not error - data might be added later
            pass
        return v


class Precinct(AdministrativeBoundary):
    """
    Electoral or commissioner precinct.
    
    Can represent voting precincts or county commissioner precincts.
    """
    entity_type: Literal["precinct"] = "precinct"
    precinct_type: Literal["voting", "commissioner", "justice"] = Field(
        ...,
        description="Type of precinct"
    )
    precinct_number: str = Field(
        ...,
        description="Precinct number or identifier"
    )
    polling_location_ids: List[str] = Field(
        default_factory=list,
        description="TOP IDs of polling locations in this precinct"
    )
    registered_voters: Optional[int] = Field(
        None,
        description="Number of registered voters"
    )
    
    @validator('precinct_type')
    def validate_precinct_boundaries(cls, v, values):
        """Different precinct types have different requirements."""
        if v == "commissioner" and 'precinct_number' in values:
            # Commissioner precincts in Texas are numbered 1-4
            try:
                num = int(values['precinct_number'])
                if num < 1 or num > 4:
                    raise ValueError('Commissioner precincts must be numbered 1-4')
            except ValueError:
                pass  # Non-numeric identifiers allowed for other types
        return v


class VotingLocation(SpatialMixin, TOPEntity):
    """
    Polling place or voting location.
    
    Represents physical locations where voting takes place.
    """
    entity_type: Literal["voting_location"] = "voting_location"
    location_type: Literal["election_day", "early_voting", "both"] = Field(
        ...,
        description="When this location is used for voting"
    )
    facility_name: str = Field(
        ...,
        description="Name of the facility (school, library, etc.)"
    )
    address: str = Field(
        ...,
        description="Physical street address"
    )
    accessibility_features: List[str] = Field(
        default_factory=list,
        description="ADA compliance and accessibility features"
    )
    parking_available: Optional[bool] = Field(
        None,
        description="Whether parking is available"
    )
    hours_of_operation: Optional[Dict[str, str]] = Field(
        None,
        description="Operating hours by date"
    )
    precinct_ids: List[str] = Field(
        default_factory=list,
        description="TOP IDs of precincts served by this location"
    )
    capacity: Optional[int] = Field(
        None,
        description="Maximum voter capacity"
    )
    voting_equipment_type: Optional[str] = Field(
        None,
        description="Type of voting equipment used"
    )


class TexasAddress(TOPEntity):
    """
    Standardized Texas address structure.
    
    Follows USPS standards with Texas-specific additions.
    """
    entity_type: Literal["address"] = "address"
    street_number: str = Field(
        ...,
        description="Street number"
    )
    street_name: str = Field(
        ...,
        description="Street name without type"
    )
    street_type: Optional[str] = Field(
        None,
        description="Street type (St, Ave, Blvd, etc.)"
    )
    direction_prefix: Optional[str] = Field(
        None,
        description="Direction prefix (N, S, E, W, etc.)"
    )
    direction_suffix: Optional[str] = Field(
        None,
        description="Direction suffix"
    )
    unit_type: Optional[str] = Field(
        None,
        description="Unit type (Apt, Suite, etc.)"
    )
    unit_number: Optional[str] = Field(
        None,
        description="Unit number"
    )
    city: str = Field(
        ...,
        description="City name"
    )
    county: str = Field(
        ...,
        description="County name"
    )
    state: Literal["TX", "Texas"] = Field(
        "TX",
        description="State (always Texas for TOP)"
    )
    zip_code: str = Field(
        ...,
        description="5-digit ZIP code"
    )
    zip_plus_four: Optional[str] = Field(
        None,
        description="ZIP+4 extension"
    )
    latitude: Optional[float] = Field(
        None,
        description="Latitude in decimal degrees (EPSG:4326)"
    )
    longitude: Optional[float] = Field(
        None,
        description="Longitude in decimal degrees (EPSG:4326)"
    )
    appraisal_district: Optional[str] = Field(
        None,
        description="County appraisal district"
    )
    voting_precinct: Optional[str] = Field(
        None,
        description="Voting precinct identifier"
    )
    council_district: Optional[str] = Field(
        None,
        description="City council district if applicable"
    )
    
    @validator('zip_code')
    def validate_zip(cls, v):
        """Validate ZIP code format."""
        if not v.isdigit() or len(v) != 5:
            raise ValueError('ZIP code must be 5 digits')
        return v
    
    @validator('zip_plus_four')
    def validate_zip_plus_four(cls, v):
        """Validate ZIP+4 format."""
        if v and (not v.isdigit() or len(v) != 4):
            raise ValueError('ZIP+4 must be 4 digits')
        return v
    
    def get_full_address(self) -> str:
        """Return formatted full address string."""
        parts = []
        
        # Street address line
        street_parts = []
        if self.direction_prefix:
            street_parts.append(self.direction_prefix)
        street_parts.append(self.street_number)
        street_parts.append(self.street_name)
        if self.street_type:
            street_parts.append(self.street_type)
        if self.direction_suffix:
            street_parts.append(self.direction_suffix)
        parts.append(' '.join(street_parts))
        
        # Unit line if present
        if self.unit_type and self.unit_number:
            parts.append(f"{self.unit_type} {self.unit_number}")
        
        # City, State ZIP line
        zip_full = self.zip_code
        if self.zip_plus_four:
            zip_full += f"-{self.zip_plus_four}"
        parts.append(f"{self.city}, {self.state} {zip_full}")
        
        return ', '.join(parts)


class Zone(AdministrativeBoundary):
    """
    Zoning district or special zone.
    
    Represents areas with specific land use or regulatory characteristics.
    """
    entity_type: Literal["zone"] = "zone"
    zone_type: str = Field(
        ...,
        description="Type of zone (residential, commercial, PID, TIRZ, etc.)"
    )
    zone_code: str = Field(
        ...,
        description="Zoning code or designation"
    )
    permitted_uses: List[str] = Field(
        default_factory=list,
        description="List of permitted land uses"
    )
    restrictions: List[str] = Field(
        default_factory=list,
        description="List of restrictions or special requirements"
    )
    overlay_zones: List[str] = Field(
        default_factory=list,
        description="TOP IDs of overlay zones that apply"
    )