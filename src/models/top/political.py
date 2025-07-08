"""
Political position and role models for Texas Ontology Protocol (TOP).

Implements positions, terms of office, and election cycles specific to
Texas governmental structures.
"""

from typing import Optional, Literal, List
from datetime import datetime
from pydantic import Field, validator
from .base import TOPEntity


class Position(TOPEntity):
    """
    Base class for political positions in Texas government.
    
    Represents both elected and appointed positions.
    """
    entity_type: Literal["position"] = "position"
    position_type: str = Field(
        ...,
        description="Type of position (elected or appointed)"
    )
    government_entity_id: str = Field(
        ...,
        description="TOP ID of the government entity this position belongs to"
    )
    title: str = Field(
        ...,
        description="Official title of the position"
    )
    responsibilities: List[str] = Field(
        default_factory=list,
        description="Key responsibilities of the position"
    )
    salary_range: Optional[str] = Field(
        None,
        description="Salary range for the position"
    )
    term_length_years: Optional[float] = Field(
        None,
        description="Standard term length in years"
    )
    term_limit: Optional[int] = Field(
        None,
        description="Maximum number of consecutive terms allowed"
    )
    requires_residency: bool = Field(
        True,
        description="Whether position requires residency in jurisdiction"
    )
    

class ElectedPosition(Position):
    """
    Elected political position in Texas government.
    
    Positions filled through public elections.
    """
    position_type: Literal["elected"] = "elected"
    election_type: Literal["at-large", "district", "precinct"] = Field(
        ...,
        description="Type of election (at-large, by district, etc.)"
    )
    district_id: Optional[str] = Field(
        None,
        description="TOP ID of district/precinct if position is district-based"
    )
    filing_deadline_days_before: Optional[int] = Field(
        None,
        description="Days before election that filing deadline occurs"
    )
    partisan: bool = Field(
        False,
        description="Whether this is a partisan position"
    )
    next_election_date: Optional[datetime] = Field(
        None,
        description="Date of next scheduled election for this position"
    )


class AppointedPosition(Position):
    """
    Appointed political position in Texas government.
    
    Positions filled through appointment by elected officials or boards.
    """
    position_type: Literal["appointed"] = "appointed"
    appointing_authority: str = Field(
        ...,
        description="Entity or position with authority to make appointment"
    )
    requires_confirmation: bool = Field(
        False,
        description="Whether appointment requires confirmation (e.g., by council)"
    )
    confirming_body: Optional[str] = Field(
        None,
        description="Body that must confirm appointment if required"
    )
    serves_at_pleasure: bool = Field(
        True,
        description="Whether appointee serves at pleasure of appointing authority"
    )


class Mayor(ElectedPosition):
    """Mayor position in Texas municipalities."""
    entity_type: Literal["mayor"] = "mayor"
    mayor_type: Literal["strong", "weak", "ceremonial"] = Field(
        "weak",
        description="Type of mayoral system"
    )
    voting_member_of_council: bool = Field(
        True,
        description="Whether mayor votes on council matters"
    )
    veto_power: bool = Field(
        False,
        description="Whether mayor has veto power over council actions"
    )


class CouncilMember(ElectedPosition):
    """City council member position."""
    entity_type: Literal["council_member"] = "council_member"
    place_number: Optional[int] = Field(
        None,
        description="Place number for at-large positions"
    )
    committee_assignments: List[str] = Field(
        default_factory=list,
        description="Current committee assignments"
    )


class CityManager(AppointedPosition):
    """
    City Manager position in council-manager governments.
    
    Chief administrative officer appointed by city council.
    """
    entity_type: Literal["city_manager"] = "city_manager"
    appointing_authority: Literal["city_council"] = "city_council"
    charter_powers: List[str] = Field(
        default_factory=list,
        description="Specific powers granted by city charter"
    )
    department_oversight: List[str] = Field(
        default_factory=list,
        description="Departments under direct oversight"
    )


class CountyJudge(ElectedPosition):
    """
    County Judge - chief executive of Texas county.
    
    Unique Texas position that serves as both administrative head
    and presiding officer of commissioners court.
    """
    entity_type: Literal["county_judge"] = "county_judge"
    election_type: Literal["at-large"] = "at-large"
    judicial_duties: bool = Field(
        True,
        description="Whether position includes judicial responsibilities"
    )
    emergency_management_coordinator: bool = Field(
        True,
        description="Whether serves as emergency management coordinator"
    )


class Commissioner(ElectedPosition):
    """County Commissioner representing a precinct."""
    entity_type: Literal["commissioner"] = "commissioner"
    election_type: Literal["precinct"] = "precinct"
    precinct_number: int = Field(
        ...,
        description="Precinct number (1-4)"
    )
    road_maintenance_budget: Optional[float] = Field(
        None,
        description="Annual road maintenance budget for precinct"
    )
    
    @validator('precinct_number')
    def validate_precinct_number(cls, v):
        """Texas counties have 4 commissioner precincts."""
        if v < 1 or v > 4:
            raise ValueError('Precinct number must be between 1 and 4')
        return v


class Term(TOPEntity):
    """
    Term of office for an elected or appointed official.
    
    Represents a specific period during which a person holds a position.
    """
    entity_type: Literal["term"] = "term"
    position_id: str = Field(
        ...,
        description="TOP ID of the position"
    )
    office_holder_id: str = Field(
        ...,
        description="TOP ID of the person holding the position"
    )
    term_number: Optional[int] = Field(
        None,
        description="Which term this is for the office holder (1st, 2nd, etc.)"
    )
    start_date: datetime = Field(
        ...,
        description="Date term began"
    )
    scheduled_end_date: datetime = Field(
        ...,
        description="Scheduled end date of term"
    )
    actual_end_date: Optional[datetime] = Field(
        None,
        description="Actual end date if term ended early"
    )
    end_reason: Optional[str] = Field(
        None,
        description="Reason term ended (completed, resigned, recalled, etc.)"
    )
    oath_date: Optional[datetime] = Field(
        None,
        description="Date oath of office was administered"
    )
    
    @validator('actual_end_date')
    def validate_end_date(cls, v, values):
        """Ensure actual end date is not after scheduled end date."""
        if v and 'scheduled_end_date' in values and v > values['scheduled_end_date']:
            raise ValueError('Actual end date cannot be after scheduled end date')
        return v


class ElectionCycle(TOPEntity):
    """
    Election cycle for Texas uniform election dates.
    
    Texas has specific uniform election dates that most local
    elections must follow.
    """
    entity_type: Literal["election_cycle"] = "election_cycle"
    election_date: datetime = Field(
        ...,
        description="Date of the election"
    )
    election_type: Literal["general", "special", "runoff"] = Field(
        ...,
        description="Type of election"
    )
    uniform_date_type: Optional[Literal["may", "november"]] = Field(
        None,
        description="Which uniform election date this follows"
    )
    positions_up_for_election: List[str] = Field(
        default_factory=list,
        description="TOP IDs of positions on ballot"
    )
    voter_registration_deadline: datetime = Field(
        ...,
        description="Deadline for voter registration"
    )
    early_voting_start: Optional[datetime] = Field(
        None,
        description="First day of early voting"
    )
    early_voting_end: Optional[datetime] = Field(
        None,
        description="Last day of early voting"
    )
    
    @validator('election_date')
    def validate_uniform_date(cls, v, values):
        """Validate election date follows Texas uniform election date rules."""
        # May uniform date: First Saturday in May (odd years for most municipalities)
        # November uniform date: First Tuesday after first Monday in November
        # This is a simplified check - full implementation would verify exact dates
        month = v.month
        if month not in [5, 11]:
            # Special elections can be on other dates but should be noted
            if values.get('election_type') != 'special':
                raise ValueError('General elections must be in May or November per Texas uniform date law')
        return v