"""
Legal document models for Texas Ontology Protocol (TOP).

Implements various types of legal documents used in Texas government
including ordinances, resolutions, charters, and other official documents.
"""

from typing import Optional, Literal, List, Dict, Any
from datetime import datetime
from pydantic import Field, validator, HttpUrl
from .base import TOPEntity


class LegalDocument(TOPEntity):
    """
    Base class for legal documents in Texas government.
    
    Represents official documents with legal significance.
    """
    entity_type: Literal["legal_document"] = "legal_document"
    document_type: str = Field(
        ...,
        description="Type of legal document"
    )
    document_number: str = Field(
        ...,
        description="Official document number or identifier"
    )
    title: str = Field(
        ...,
        description="Official title of the document"
    )
    document_summary: Optional[str] = Field(
        None,
        description="Brief summary of the document's purpose and content"
    )
    full_text: Optional[str] = Field(
        None,
        description="Complete text of the document"
    )
    document_url: Optional[HttpUrl] = Field(
        None,
        description="URL where document can be accessed"
    )
    issuing_entity_id: str = Field(
        ...,
        description="TOP ID of the government entity that issued the document"
    )
    approval_date: datetime = Field(
        ...,
        description="Date the document was approved"
    )
    effective_date: datetime = Field(
        ...,
        description="Date the document becomes effective"
    )
    expiration_date: Optional[datetime] = Field(
        None,
        description="Date the document expires if applicable"
    )
    vote_record: Optional[Dict[str, Any]] = Field(
        None,
        description="Voting record (for, against, abstain, absent)"
    )
    sponsors: List[str] = Field(
        default_factory=list,
        description="TOP IDs of officials who sponsored the document"
    )
    amendments: List[str] = Field(
        default_factory=list,
        description="TOP IDs of documents that amend this one"
    )
    repeals: List[str] = Field(
        default_factory=list,
        description="TOP IDs of documents this one repeals"
    )
    references: List[str] = Field(
        default_factory=list,
        description="Citations to other legal documents or codes"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Subject matter tags for categorization"
    )
    
    @validator('effective_date')
    def validate_effective_date(cls, v, values):
        """Ensure effective date is not before approval date."""
        if 'approval_date' in values and v < values['approval_date']:
            raise ValueError('Effective date cannot be before approval date')
        return v


class Ordinance(LegalDocument):
    """
    Municipal ordinance - local law passed by city council.
    
    Ordinances have the force of law within city limits.
    """
    entity_type: Literal["ordinance"] = "ordinance"
    document_type: Literal["ordinance"] = "ordinance"
    ordinance_type: Literal["general", "emergency", "zoning", "charter"] = Field(
        "general",
        description="Type of ordinance"
    )
    code_section: Optional[str] = Field(
        None,
        description="Municipal code section this ordinance affects"
    )
    penalty_provision: Optional[str] = Field(
        None,
        description="Penalties for violation if applicable"
    )
    readings: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Record of readings (date, vote, etc.)"
    )
    public_hearing_date: Optional[datetime] = Field(
        None,
        description="Date of public hearing if required"
    )
    
    @validator('readings')
    def validate_readings(cls, v, values):
        """Most ordinances require multiple readings."""
        if values.get('ordinance_type') != 'emergency' and len(v) < 2:
            # Warning - emergency ordinances may have single reading
            pass
        return v


class Resolution(LegalDocument):
    """
    Resolution - formal expression of opinion or intent.
    
    Resolutions typically don't have the force of law but express
    policy or authorize specific actions.
    """
    entity_type: Literal["resolution"] = "resolution"
    document_type: Literal["resolution"] = "resolution"
    resolution_type: str = Field(
        ...,
        description="Type of resolution (policy, honorary, administrative, etc.)"
    )
    whereas_clauses: List[str] = Field(
        default_factory=list,
        description="List of whereas clauses providing context"
    )
    resolved_clauses: List[str] = Field(
        default_factory=list,
        description="List of resolved clauses stating actions"
    )
    is_binding: bool = Field(
        False,
        description="Whether resolution has binding effect"
    )


class Charter(LegalDocument):
    """
    City Charter - fundamental governing document for home-rule cities.
    
    Charters define the structure and powers of city government.
    """
    entity_type: Literal["charter"] = "charter"
    document_type: Literal["charter"] = "charter"
    adoption_method: Literal["voter_approved", "legislative"] = Field(
        "voter_approved",
        description="How the charter was adopted"
    )
    election_date: Optional[datetime] = Field(
        None,
        description="Date of election if voter approved"
    )
    vote_results: Optional[Dict[str, int]] = Field(
        None,
        description="Voting results (for, against)"
    )
    articles: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of charter articles with titles"
    )
    charter_review_required: Optional[datetime] = Field(
        None,
        description="Date when charter review is required"
    )
    home_rule_election_date: Optional[datetime] = Field(
        None,
        description="Date city voted to become home-rule"
    )


class Proclamation(LegalDocument):
    """
    Proclamation - ceremonial or honorary declaration.
    
    Used for recognitions, declarations of special days/months, etc.
    """
    entity_type: Literal["proclamation"] = "proclamation"
    document_type: Literal["proclamation"] = "proclamation"
    proclamation_type: Literal["honorary", "emergency", "administrative"] = Field(
        "honorary",
        description="Type of proclamation"
    )
    honoree: Optional[str] = Field(
        None,
        description="Person or organization being honored"
    )
    occasion: Optional[str] = Field(
        None,
        description="Occasion or event being proclaimed"
    )
    duration: Optional[str] = Field(
        None,
        description="Duration of proclamation (day, week, month)"
    )


class ExecutiveOrder(LegalDocument):
    """
    Executive Order - directive issued by mayor or county judge.
    
    Used for administrative directives and emergency declarations.
    """
    entity_type: Literal["executive_order"] = "executive_order"
    document_type: Literal["executive_order"] = "executive_order"
    order_type: Literal["administrative", "emergency", "disaster"] = Field(
        "administrative",
        description="Type of executive order"
    )
    issuing_official_id: str = Field(
        ...,
        description="TOP ID of the official issuing the order"
    )
    legal_authority: str = Field(
        ...,
        description="Legal basis for issuing the order"
    )
    directives: List[str] = Field(
        default_factory=list,
        description="Specific directives contained in the order"
    )
    affected_departments: List[str] = Field(
        default_factory=list,
        description="Departments affected by the order"
    )
    termination_condition: Optional[str] = Field(
        None,
        description="Condition that terminates the order"
    )


class Contract(LegalDocument):
    """
    Government contract or agreement.
    
    Represents contracts between government entities and other parties.
    """
    entity_type: Literal["contract"] = "contract"
    document_type: Literal["contract"] = "contract"
    contract_type: str = Field(
        ...,
        description="Type of contract (service, construction, interlocal, etc.)"
    )
    parties: List[str] = Field(
        ...,
        description="All parties to the contract"
    )
    contract_value: Optional[float] = Field(
        None,
        description="Total value of the contract in USD"
    )
    payment_terms: Optional[str] = Field(
        None,
        description="Payment terms and schedule"
    )
    performance_period_start: datetime = Field(
        ...,
        description="Start of performance period"
    )
    performance_period_end: datetime = Field(
        ...,
        description="End of performance period"
    )
    renewable: bool = Field(
        False,
        description="Whether contract is renewable"
    )
    renewal_terms: Optional[str] = Field(
        None,
        description="Terms for renewal if applicable"
    )
    procurement_method: Optional[str] = Field(
        None,
        description="How contract was procured (RFP, sole source, etc.)"
    )
    
    @validator('parties')
    def validate_parties(cls, v):
        """Contract must have at least two parties."""
        if len(v) < 2:
            raise ValueError('Contract must have at least two parties')
        return v


class Permit(LegalDocument):
    """
    Permit or license issued by government.
    
    Represents various permits issued for activities within jurisdiction.
    """
    entity_type: Literal["permit"] = "permit"
    document_type: Literal["permit"] = "permit"
    permit_type: str = Field(
        ...,
        description="Type of permit (building, special event, alcohol, etc.)"
    )
    applicant_name: str = Field(
        ...,
        description="Name of permit applicant"
    )
    location_address: Optional[str] = Field(
        None,
        description="Address where permitted activity will occur"
    )
    conditions: List[str] = Field(
        default_factory=list,
        description="Special conditions or restrictions"
    )
    fee_amount: Optional[float] = Field(
        None,
        description="Permit fee amount in USD"
    )
    inspection_required: bool = Field(
        False,
        description="Whether inspection is required"
    )
    inspection_dates: List[datetime] = Field(
        default_factory=list,
        description="Scheduled or completed inspection dates"
    )