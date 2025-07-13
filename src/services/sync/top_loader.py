"""
TOP-compliant data loader for Fort Worth municipal data.

This module provides comprehensive loading of Fort Worth data
with full Texas Ontology Protocol compliance using structured outputs.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from graphiti_core.nodes import EpisodeType
from graphiti_core.utils.bulk_utils import RawEpisode

from src.models.top.structured import (
    TOPEpisodeData,
    StructuredEntity,
    StructuredRelationship,
    TOPEntityType,
    TOPRelationshipType,
    ConfidenceLevel
)
from src.models.ontology import add_episode as add_ontology_episode

logger = logging.getLogger(__name__)


class TOPDataLoader:
    """Loads Fort Worth data with full TOP compliance."""
    
    def __init__(self, graphiti):
        self.graphiti = graphiti
        self.created_entities = {}  # Track created entities by TOP ID
        
    async def create_base_entities(self) -> TOPEpisodeData:
        """Create the foundational Fort Worth entities."""
        episode = TOPEpisodeData()
        
        # Create Fort Worth city entity
        fort_worth = StructuredEntity(
            entity_type=TOPEntityType.HOME_RULE_CITY,
            top_id="fwtx:city:fort-worth",
            properties={
                "entity_name": "City of Fort Worth",
                "population": 956709,
                "incorporation_date": "1873-03-19",
                "charter_adopted": "1924-01-01",
                "governmental_form": "council-manager",
                "website": "https://fortworthtexas.gov",
                "county": "Tarrant County",
                "state": "Texas",
                "area_sq_miles": 349.2,
                "time_zone": "CST/CDT",
                "fips_code": "4827000"
            },
            source="https://fortworthtexas.gov",
            confidence=ConfidenceLevel.HIGH,
            valid_from="1873-03-19"
        )
        episode.entities.append(fort_worth)
        self.created_entities[fort_worth.top_id] = fort_worth
        
        # Create Tarrant County entity
        tarrant_county = StructuredEntity(
            entity_type=TOPEntityType.COUNTY,
            top_id="fwtx:county:tarrant",
            properties={
                "entity_name": "Tarrant County",
                "population": 2110640,
                "county_seat": "Fort Worth",
                "established": "1849-12-20",
                "website": "https://www.tarrantcounty.com",
                "area_sq_miles": 897
            },
            source="https://www.tarrantcounty.com",
            confidence=ConfidenceLevel.HIGH,
            valid_from="1849-12-20"
        )
        episode.entities.append(tarrant_county)
        self.created_entities[tarrant_county.top_id] = tarrant_county
        
        # Create relationship: Fort Worth is part of Tarrant County
        rel = StructuredRelationship(
            relationship_type=TOPRelationshipType.PART_OF,
            source_entity=fort_worth.top_id,
            target_entity=tarrant_county.top_id,
            properties={
                "relationship_type": "county_seat",
                "since": "1849-12-20"
            },
            source="https://www.tarrantcounty.com",
            confidence=ConfidenceLevel.HIGH,
            valid_from="1849-12-20"
        )
        episode.relationships.append(rel)
        
        return episode
    
    async def create_government_structure(self) -> TOPEpisodeData:
        """Create government structure entities."""
        episode = TOPEpisodeData()
        
        # Mayor position
        mayor = StructuredEntity(
            entity_type=TOPEntityType.MAYOR,
            top_id="fwtx:mayor:current",
            properties={
                "entity_name": "Mayor Mattie Parker",
                "person_name": "Mattie Parker",
                "term_start": "2021-06-01",
                "term_end": "2025-05-31",
                "election_type": "at-large",
                "political_party": "Republican",
                "salary": 29000,
                "contact_email": "mayor@fortworthtexas.gov",
                "office_location": "City Hall, 200 Texas St"
            },
            source="https://fortworthtexas.gov/government/mayor",
            confidence=ConfidenceLevel.HIGH,
            valid_from="2021-06-01"
        )
        episode.entities.append(mayor)
        
        # Mayor governs the city
        governs = StructuredRelationship(
            relationship_type=TOPRelationshipType.GOVERNS,
            source_entity=mayor.top_id,
            target_entity="fwtx:city:fort-worth",
            properties={
                "elected": "2021-05-01",
                "role": "chief_executive"
            },
            source="https://fortworthtexas.gov/government/mayor",
            confidence=ConfidenceLevel.HIGH,
            valid_from="2021-06-01"
        )
        episode.relationships.append(governs)
        
        # City Manager position
        city_manager = StructuredEntity(
            entity_type=TOPEntityType.CITY_MANAGER,
            top_id="fwtx:citymanager:current",
            properties={
                "entity_name": "City Manager David Cooke",
                "person_name": "David Cooke",
                "appointment_date": "2014-02-01",
                "salary": 375000,
                "reports_to": "City Council",
                "responsibilities": "Chief administrative officer"
            },
            source="https://fortworthtexas.gov/citymanager",
            confidence=ConfidenceLevel.HIGH,
            valid_from="2014-02-01"
        )
        episode.entities.append(city_manager)
        
        # City Manager appointed by Mayor/Council
        appointed = StructuredRelationship(
            relationship_type=TOPRelationshipType.APPOINTED_BY,
            source_entity=city_manager.top_id,
            target_entity=mayor.top_id,
            properties={
                "approved_by": "City Council",
                "appointment_date": "2014-02-01"
            },
            source="https://fortworthtexas.gov/citymanager",
            confidence=ConfidenceLevel.HIGH,
            valid_from="2014-02-01"
        )
        episode.relationships.append(appointed)
        
        return episode
    
    async def create_council_districts(self) -> TOPEpisodeData:
        """Create council districts and members."""
        episode = TOPEpisodeData()
        
        # Council district data (current as of 2024)
        council_data = [
            {"district": 1, "member": "Carlos Flores", "population": 95000},
            {"district": 2, "member": "Andrew Piel", "population": 97000},
            {"district": 3, "member": "Michael D. Crain", "population": 96000},
            {"district": 4, "member": "Alan Blaylock", "population": 94000},
            {"district": 5, "member": "Gyna Bivens", "population": 98000},
            {"district": 6, "member": "Jared Williams", "population": 95000},
            {"district": 7, "member": "Leonard Firestone", "population": 96000},
            {"district": 8, "member": "Chris Nettles", "population": 97000},
            {"district": 9, "member": "Elizabeth M. Beck", "population": 95000}
        ]
        
        for data in council_data:
            # Create district entity
            district = StructuredEntity(
                entity_type=TOPEntityType.COUNCIL_DISTRICT,
                top_id=f"fwtx:district:{data['district']}",
                properties={
                    "entity_name": f"Fort Worth Council District {data['district']}",
                    "district_number": data['district'],
                    "population": data['population'],
                    "established_date": "2022-01-01",  # Last redistricting
                    "geographic_area": f"District {data['district']} boundaries"
                },
                source="https://fortworthtexas.gov/government/city-council",
                confidence=ConfidenceLevel.HIGH,
                valid_from="2022-01-01"
            )
            episode.entities.append(district)
            
            # Create council member
            member = StructuredEntity(
                entity_type=TOPEntityType.COUNCIL_MEMBER,
                top_id=f"fwtx:councilmember:district-{data['district']}",
                properties={
                    "entity_name": f"Council Member {data['member']}",
                    "person_name": data['member'],
                    "district_number": data['district'],
                    "term_start": "2023-06-01",
                    "term_end": "2025-05-31",
                    "election_type": "single-member-district",
                    "salary": 25000,
                    "office_location": "City Hall"
                },
                source="https://fortworthtexas.gov/government/city-council",
                confidence=ConfidenceLevel.HIGH,
                valid_from="2023-06-01"
            )
            episode.entities.append(member)
            
            # Council member serves district
            serves = StructuredRelationship(
                relationship_type=TOPRelationshipType.SERVES,
                source_entity=member.top_id,
                target_entity=district.top_id,
                properties={
                    "elected": "2023-05-06",
                    "role": "representative"
                },
                source="https://fortworthtexas.gov/government/city-council",
                confidence=ConfidenceLevel.HIGH,
                valid_from="2023-06-01"
            )
            episode.relationships.append(serves)
            
            # District is part of city
            part_of = StructuredRelationship(
                relationship_type=TOPRelationshipType.PART_OF,
                source_entity=district.top_id,
                target_entity="fwtx:city:fort-worth",
                properties={
                    "type": "administrative_division"
                },
                source="https://fortworthtexas.gov/government/city-council",
                confidence=ConfidenceLevel.HIGH,
                valid_from="2022-01-01"
            )
            episode.relationships.append(part_of)
        
        return episode
    
    async def create_city_departments(self) -> TOPEpisodeData:
        """Create major city departments."""
        episode = TOPEpisodeData()
        
        departments = [
            {
                "id": "police",
                "name": "Fort Worth Police Department",
                "type": "public_safety",
                "chief": "Neil Noakes",
                "budget": 328000000,
                "employees": 1700,
                "established": "1873-01-01"
            },
            {
                "id": "fire",
                "name": "Fort Worth Fire Department",
                "type": "public_safety",
                "chief": "Jim Davis",
                "budget": 185000000,
                "employees": 1000,
                "established": "1873-01-01"
            },
            {
                "id": "water",
                "name": "Fort Worth Water Department",
                "type": "utility",
                "director": "Chris Harder",
                "budget": 500000000,
                "employees": 650,
                "established": "1882-01-01"
            },
            {
                "id": "code",
                "name": "Code Compliance Department",
                "type": "regulatory",
                "director": "Brandon Bennett",
                "budget": 18000000,
                "employees": 200,
                "established": "1985-01-01"
            },
            {
                "id": "development",
                "name": "Development Services Department",
                "type": "planning",
                "director": "D'Arcy Young Jr.",
                "budget": 25000000,
                "employees": 180,
                "established": "1990-01-01"
            }
        ]
        
        for dept in departments:
            entity = StructuredEntity(
                entity_type=TOPEntityType.DEPARTMENT,
                top_id=f"fwtx:dept:{dept['id']}",
                properties={
                    "entity_name": dept['name'],
                    "department_type": dept['type'],
                    "department_head": dept.get('chief', dept.get('director')),
                    "budget_fy2024": dept['budget'],
                    "employee_count": dept['employees'],
                    "parent_organization": "fwtx:city:fort-worth",
                    "website": f"https://fortworthtexas.gov/departments/{dept['id']}"
                },
                source="https://fortworthtexas.gov/departments",
                confidence=ConfidenceLevel.HIGH,
                valid_from=dept['established']
            )
            episode.entities.append(entity)
            
            # Department is part of city
            part_of = StructuredRelationship(
                relationship_type=TOPRelationshipType.PART_OF,
                source_entity=entity.top_id,
                target_entity="fwtx:city:fort-worth",
                properties={
                    "relationship_type": "administrative",
                    "oversight": "City Manager"
                },
                source="https://fortworthtexas.gov/departments",
                confidence=ConfidenceLevel.HIGH,
                valid_from=dept['established']
            )
            episode.relationships.append(part_of)
        
        return episode
    
    async def create_legal_documents(self) -> TOPEpisodeData:
        """Create legal document entities."""
        episode = TOPEpisodeData()
        
        # City Charter
        charter = StructuredEntity(
            entity_type=TOPEntityType.CHARTER,
            top_id="fwtx:charter:1924",
            properties={
                "entity_name": "Fort Worth City Charter",
                "document_number": "Charter-1924",
                "title": "Charter of the City of Fort Worth",
                "date_adopted": "1924-01-01",
                "effective_date": "1924-01-01",
                "adopted_by": "City of Fort Worth",
                "amendments": 150,
                "legal_authority": "Texas Local Government Code",
                "document_url": "https://fortworthtexas.gov/charter"
            },
            source="https://fortworthtexas.gov/charter",
            confidence=ConfidenceLevel.HIGH,
            valid_from="1924-01-01"
        )
        episode.entities.append(charter)
        
        # Charter governs the city
        governs = StructuredRelationship(
            relationship_type=TOPRelationshipType.GOVERNS,
            source_entity=charter.top_id,
            target_entity="fwtx:city:fort-worth",
            properties={
                "authority": "home-rule",
                "legal_basis": "Texas Constitution Article XI"
            },
            source="https://fortworthtexas.gov/charter",
            confidence=ConfidenceLevel.HIGH,
            valid_from="1924-01-01"
        )
        episode.relationships.append(governs)
        
        return episode
    
    async def load_all_top_data(self) -> List[RawEpisode]:
        """Load all Fort Worth data with TOP compliance."""
        episodes = []
        
        try:
            # Add initial episode for schema
            await add_ontology_episode(self.graphiti, episode_type="government")
            
            # Create base entities
            logger.info("Creating base Fort Worth entities...")
            base_episode = await self.create_base_entities()
            episodes.append(RawEpisode(
                name="Fort Worth Base Entities",
                content=base_episode.to_episode_content(),
                source=EpisodeType.json,
                source_description="TOP-compliant Fort Worth city data",
                reference_time=datetime.now()
            ))
            
            # Create government structure
            logger.info("Creating government structure...")
            gov_episode = await self.create_government_structure()
            episodes.append(RawEpisode(
                name="Fort Worth Government Structure",
                content=gov_episode.to_episode_content(),
                source=EpisodeType.json,
                source_description="TOP-compliant government structure",
                reference_time=datetime.now()
            ))
            
            # Create council districts
            logger.info("Creating council districts...")
            council_episode = await self.create_council_districts()
            episodes.append(RawEpisode(
                name="Fort Worth Council Districts",
                content=council_episode.to_episode_content(),
                source=EpisodeType.json,
                source_description="TOP-compliant council districts",
                reference_time=datetime.now()
            ))
            
            # Create departments
            logger.info("Creating city departments...")
            dept_episode = await self.create_city_departments()
            episodes.append(RawEpisode(
                name="Fort Worth City Departments",
                content=dept_episode.to_episode_content(),
                source=EpisodeType.json,
                source_description="TOP-compliant department data",
                reference_time=datetime.now()
            ))
            
            # Create legal documents
            logger.info("Creating legal documents...")
            legal_episode = await self.create_legal_documents()
            episodes.append(RawEpisode(
                name="Fort Worth Legal Documents",
                content=legal_episode.to_episode_content(),
                source=EpisodeType.json,
                source_description="TOP-compliant legal documents",
                reference_time=datetime.now()
            ))
            
            logger.info(f"Created {len(episodes)} TOP-compliant episodes")
            
        except Exception as e:
            logger.error(f"Error creating TOP data: {e}")
            raise
        
        return episodes
    
    async def sync_to_graphiti(self):
        """Sync all TOP data to Graphiti."""
        logger.info("Starting TOP-compliant Fort Worth data sync...")
        
        episodes = await self.load_all_top_data()
        
        if episodes:
            await self.graphiti.add_episode_bulk(episodes)
            logger.info(f"Successfully synced {len(episodes)} episodes to Graphiti")
            
            # Build communities
            logger.info("Building communities...")
            await self.graphiti.build_communities()
            logger.info("Community building completed")
        else:
            logger.warning("No episodes created for sync")


# Convenience function
async def load_top_compliant_data(graphiti):
    """Load Fort Worth data with full TOP compliance."""
    loader = TOPDataLoader(graphiti)
    await loader.sync_to_graphiti()