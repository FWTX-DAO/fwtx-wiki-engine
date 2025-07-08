"""
Government entity models for Texas Ontology Protocol (TOP).

Implements Texas-specific governmental structures including home-rule cities,
council-manager forms of government, and county structures.
"""

from typing import Optional, List, Literal
from pydantic import Field, validator
from .base import TOPEntity, SpatialMixin


class GovernmentEntity(SpatialMixin, TOPEntity):
    """
    Base class for all governmental organizations in Texas.
    
    Serves as the foundation for municipalities, counties, and other
    governmental structures.
    """
    entity_type: Literal["government"] = "government"
    incorporation_date: Optional[str] = Field(
        None,
        description="Date of incorporation or establishment"
    )
    population: Optional[int] = Field(
        None,
        description="Current population count"
    )
    annual_budget: Optional[float] = Field(
        None,
        description="Annual budget in USD"
    )
    website: Optional[str] = Field(
        None,
        description="Official government website URL"
    )
    phone: Optional[str] = Field(
        None,
        description="Main contact phone number"
    )
    address: Optional[str] = Field(
        None,
        description="Primary physical address"
    )
    tax_rate: Optional[float] = Field(
        None,
        description="Current tax rate"
    )
    fiscal_year_start: Optional[str] = Field(
        None,
        description="Start of fiscal year (MM-DD format)"
    )


class Municipality(GovernmentEntity):
    """
    Base class for Texas municipalities.
    
    Represents cities, towns, and villages within Texas.
    """
    entity_type: Literal["municipality"] = "municipality"
    municipality_type: str = Field(
        ...,
        description="Type of municipality (city, town, village)"
    )
    county: str = Field(
        ...,
        description="County where municipality is located"
    )
    
    
class HomeRuleCity(Municipality):
    """
    Home Rule City - Texas cities with population >5,000 and adopted charter.
    
    These cities have greater autonomy and can adopt their own charters
    defining their governmental structure.
    """
    entity_type: Literal["home_rule_city"] = "home_rule_city"
    charter_adopted_date: str = Field(
        ...,
        description="Date the city charter was adopted"
    )
    charter_url: Optional[str] = Field(
        None,
        description="URL to the city charter document"
    )
    government_form: str = Field(
        "council-manager",
        description="Form of government (council-manager, mayor-council, etc.)"
    )
    council_size: int = Field(
        ...,
        description="Number of council members including mayor"
    )
    council_districts: Optional[int] = Field(
        None,
        description="Number of council districts (if applicable)"
    )
    term_limits: Optional[bool] = Field(
        None,
        description="Whether term limits exist for elected officials"
    )
    
    @validator('population')
    def validate_home_rule_population(cls, v):
        """Home rule cities must have population >5,000."""
        if v and v <= 5000:
            raise ValueError('Home rule cities must have population greater than 5,000')
        return v


class GeneralLawCity(Municipality):
    """
    General Law City - Cities operating under state law without custom charter.
    
    These cities follow templates provided by Texas state law based on
    their type and population.
    """
    entity_type: Literal["general_law_city"] = "general_law_city"
    city_classification: Literal["Type A", "Type B", "Type C"] = Field(
        ...,
        description="General law city classification per Texas Local Government Code"
    )
    aldermanic_form: Optional[bool] = Field(
        None,
        description="Whether city uses aldermanic form of government"
    )
    
    @validator('city_classification')
    def validate_classification_population(cls, v, values):
        """Validate city classification matches population requirements."""
        pop = values.get('population')
        if not pop:
            return v
            
        if v == "Type A" and pop < 5000:
            raise ValueError('Type A cities must have population >= 5,000')
        elif v == "Type B" and (pop < 201 or pop > 10000):
            raise ValueError('Type B cities must have population between 201-10,000')
        elif v == "Type C" and (pop < 201 or pop > 5000):
            raise ValueError('Type C cities must have population between 201-5,000')
        return v


class County(GovernmentEntity):
    """
    Texas County - One of 254 counties in Texas.
    
    Counties serve as administrative divisions and provide services
    to unincorporated areas.
    """
    entity_type: Literal["county"] = "county"
    county_seat: str = Field(
        ...,
        description="City designated as county seat"
    )
    commissioners_court_size: int = Field(
        5,
        description="Size of commissioners court (typically 5: judge + 4 commissioners)"
    )
    precincts: int = Field(
        4,
        description="Number of commissioner precincts"
    )
    unincorporated_population: Optional[int] = Field(
        None,
        description="Population living in unincorporated areas"
    )
    total_area_sq_miles: Optional[float] = Field(
        None,
        description="Total area in square miles"
    )
    
    
class Department(TOPEntity):
    """
    Government department or office within a larger entity.
    
    Represents organizational units like police, fire, public works, etc.
    """
    entity_type: Literal["department"] = "department"
    parent_entity_id: str = Field(
        ...,
        description="TOP ID of parent government entity"
    )
    department_head_position: Optional[str] = Field(
        None,
        description="Title of department head position"
    )
    employee_count: Optional[int] = Field(
        None,
        description="Number of employees"
    )
    annual_budget: Optional[float] = Field(
        None,
        description="Annual department budget in USD"
    )
    services: List[str] = Field(
        default_factory=list,
        description="List of services provided by department"
    )


class Division(TOPEntity):
    """
    Division within a government department.
    
    Represents sub-units within departments.
    """
    entity_type: Literal["division"] = "division"
    parent_department_id: str = Field(
        ...,
        description="TOP ID of parent department"
    )
    division_head_position: Optional[str] = Field(
        None,
        description="Title of division head position"
    )
    

class SpecialDistrict(GovernmentEntity):
    """
    Special purpose district in Texas.
    
    Includes water districts, hospital districts, school districts, etc.
    """
    entity_type: Literal["special_district"] = "special_district"
    district_type: str = Field(
        ...,
        description="Type of special district (water, hospital, school, etc.)"
    )
    enabling_legislation: str = Field(
        ...,
        description="State legislation that authorized the district"
    )
    service_area: List[str] = Field(
        default_factory=list,
        description="List of areas served (cities, counties, etc.)"
    )
    board_size: Optional[int] = Field(
        None,
        description="Number of board members"
    )
    elected_board: Optional[bool] = Field(
        None,
        description="Whether board members are elected"
    )


class Authority(GovernmentEntity):
    """
    Government authority or quasi-governmental entity.
    
    Includes transit authorities, housing authorities, etc.
    """
    entity_type: Literal["authority"] = "authority"
    authority_type: str = Field(
        ...,
        description="Type of authority (transit, housing, port, etc.)"
    )
    member_entities: List[str] = Field(
        default_factory=list,
        description="List of member government entities"
    )
    board_appointment_method: Optional[str] = Field(
        None,
        description="How board members are appointed"
    )