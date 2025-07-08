"""
Texas Ontology Protocol (TOP) v0.0.1

This module implements the Texas Ontology Protocol for modeling Texas municipal 
and county government structures in knowledge graphs.
"""

from .base import (
    TOPEntity, 
    TOPRelationship,
    TemporalMixin,
    SpatialMixin,
    SourceAttributionMixin
)

from .government import (
    GovernmentEntity,
    Municipality,
    HomeRuleCity,
    GeneralLawCity,
    County,
    Department,
    Division,
    SpecialDistrict,
    Authority
)

from .political import (
    ElectedPosition,
    AppointedPosition,
    Mayor,
    CouncilMember,
    CityManager,
    CountyJudge,
    Commissioner,
    Term,
    ElectionCycle
)

from .geographic import (
    AdministrativeBoundary,
    CouncilDistrict,
    Precinct,
    VotingLocation,
    TexasAddress
)

from .legal import (
    LegalDocument,
    Ordinance,
    Resolution,
    Charter,
    Proclamation,
    ExecutiveOrder
)

from .relationships import (
    Governs,
    HasJurisdictionOver,
    HoldsPosition,
    AppointedBy,
    ElectedTo,
    SupersededBy,
    PartOf,
    ReportsTo
)

__all__ = [
    # Base classes
    'TOPEntity',
    'TOPRelationship',
    'TemporalMixin',
    'SpatialMixin',
    'SourceAttributionMixin',
    
    # Government entities
    'GovernmentEntity',
    'Municipality',
    'HomeRuleCity',
    'GeneralLawCity',
    'County',
    'Department',
    'Division',
    'SpecialDistrict',
    'Authority',
    
    # Political entities
    'ElectedPosition',
    'AppointedPosition',
    'Mayor',
    'CouncilMember',
    'CityManager',
    'CountyJudge',
    'Commissioner',
    'Term',
    'ElectionCycle',
    
    # Geographic entities
    'AdministrativeBoundary',
    'CouncilDistrict',
    'Precinct',
    'VotingLocation',
    'TexasAddress',
    
    # Legal documents
    'LegalDocument',
    'Ordinance',
    'Resolution',
    'Charter',
    'Proclamation',
    'ExecutiveOrder',
    
    # Relationships
    'Governs',
    'HasJurisdictionOver',
    'HoldsPosition',
    'AppointedBy',
    'ElectedTo',
    'SupersededBy',
    'PartOf',
    'ReportsTo'
]