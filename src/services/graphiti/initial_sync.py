"""
Initial synchronization module for Fort Worth data using JSON episodes.

This module loads structured data as JSON episodes into the knowledge graph,
aligned with the Texas Ontology Protocol (TOP) strategy.
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from graphiti_core.nodes import EpisodeType
from graphiti_core.utils.bulk_utils import RawEpisode
from src.models.ontology import entity_types, edge_types, edge_type_map

logger = logging.getLogger(__name__)


class InitialDataSync:
    """Handles initial synchronization of Fort Worth municipal data."""
    
    def __init__(self, graphiti):
        self.graphiti = graphiti
        self.reference_time = datetime.now()
    
    def create_fort_worth_city_data(self) -> Dict[str, Any]:
        """Create Fort Worth city government structure data."""
        return {
            "entities": [
                {
                    "entity_type": "HomeRuleCity",
                    "top_id": "city-fort-worth-tx",
                    "properties": {
                        "entity_name": "City of Fort Worth",
                        "entity_type": "home_rule_city",
                        "population": 956709,
                        "incorporated_date": "1873-03-23",
                        "charter_adopted_date": "1924-01-01",
                        "council_size": 9,
                        "website": "https://www.fortworthtexas.gov",
                        "county": "Tarrant County",
                        "state": "Texas"
                    },
                    "source": "https://www.fortworthtexas.gov/about",
                    "confidence": "high",
                    "valid_from": "1924-01-01"
                },
                {
                    "entity_type": "Mayor",
                    "top_id": "mayor-fort-worth-2021-2025",
                    "properties": {
                        "entity_name": "Mattie Parker",
                        "position_type": "elected",
                        "term_start": "2021-06-01",
                        "term_end": "2025-05-31",
                        "election_type": "at-large",
                        "salary": 29000,
                        "term_limit": "None"
                    },
                    "source": "https://www.fortworthtexas.gov/government/mayor",
                    "confidence": "high",
                    "valid_from": "2021-06-01"
                },
                {
                    "entity_type": "CityManager",
                    "top_id": "city-manager-fort-worth-2014",
                    "properties": {
                        "entity_name": "David Cooke",
                        "position_type": "appointed",
                        "appointment_date": "2014-06-10",
                        "appointed_by": "City Council",
                        "salary": 375000
                    },
                    "source": "https://www.fortworthtexas.gov/departments/city-manager",
                    "confidence": "high",
                    "valid_from": "2014-06-10"
                }
            ],
            "relationships": [
                {
                    "relationship_type": "Governs",
                    "source_entity": "city-fort-worth-tx",
                    "target_entity": "tarrant-county-tx",
                    "properties": {
                        "jurisdiction_type": "municipal",
                        "established_date": "1873-03-23"
                    },
                    "source": "https://www.fortworthtexas.gov/about",
                    "confidence": "high"
                },
                {
                    "relationship_type": "HoldsPosition",
                    "source_entity": "mattie-parker",
                    "target_entity": "mayor-fort-worth-2021-2025",
                    "properties": {
                        "start_date": "2021-06-01",
                        "election_date": "2021-05-01"
                    },
                    "source": "https://www.fortworthtexas.gov/government/mayor",
                    "confidence": "high"
                }
            ]
        }
    
    def create_city_council_data(self) -> Dict[str, Any]:
        """Create city council members and districts data."""
        council_districts = []
        
        # Add council districts
        for i in range(2, 10):  # Districts 2-9
            council_districts.append({
                "entity_type": "CouncilDistrict",
                "top_id": f"council-district-{i}-fort-worth",
                "properties": {
                    "entity_name": f"Fort Worth City Council District {i}",
                    "district_number": i,
                    "population": 106000,  # Approximate
                    "established_date": "1977-01-01"
                },
                "source": "https://www.fortworthtexas.gov/government/city-council",
                "confidence": "high",
                "valid_from": "1977-01-01"
            })
        
        # Sample council members
        council_members = [
            {
                "entity_type": "CouncilMember",
                "top_id": "council-member-district-2-2021",
                "properties": {
                    "entity_name": "Carlos Flores",
                    "district": 2,
                    "position_type": "elected",
                    "term_start": "2021-06-01",
                    "term_end": "2025-05-31",
                    "election_type": "single-member-district"
                },
                "source": "https://www.fortworthtexas.gov/government/city-council/district-2",
                "confidence": "high",
                "valid_from": "2021-06-01"
            },
            {
                "entity_type": "CouncilMember",
                "top_id": "council-member-district-3-2021",
                "properties": {
                    "entity_name": "Michael D. Crain",
                    "district": 3,
                    "position_type": "elected",
                    "term_start": "2021-06-01",
                    "term_end": "2025-05-31",
                    "election_type": "single-member-district"
                },
                "source": "https://www.fortworthtexas.gov/government/city-council/district-3",
                "confidence": "high",
                "valid_from": "2021-06-01"
            }
        ]
        
        return {
            "entities": council_districts + council_members,
            "relationships": [
                {
                    "relationship_type": "PartOf",
                    "source_entity": f"council-district-{i}-fort-worth",
                    "target_entity": "city-fort-worth-tx",
                    "properties": {
                        "relationship_type": "administrative_subdivision"
                    },
                    "source": "https://www.fortworthtexas.gov/government/city-council",
                    "confidence": "high"
                }
                for i in range(2, 10)
            ]
        }
    
    def create_department_data(self) -> Dict[str, Any]:
        """Create city department structure data."""
        departments = [
            {
                "entity_type": "Department",
                "top_id": "dept-police-fort-worth",
                "properties": {
                    "entity_name": "Fort Worth Police Department",
                    "department_type": "public_safety",
                    "established_date": "1873-01-01",
                    "budget_fy2024": 328000000,
                    "employee_count": 1700,
                    "chief": "Neil Noakes"
                },
                "source": "https://www.fortworthpd.com",
                "confidence": "high",
                "valid_from": "1873-01-01"
            },
            {
                "entity_type": "Department",
                "top_id": "dept-fire-fort-worth",
                "properties": {
                    "entity_name": "Fort Worth Fire Department",
                    "department_type": "public_safety",
                    "established_date": "1873-01-01",
                    "budget_fy2024": 225000000,
                    "employee_count": 1000,
                    "chief": "Jim Davis"
                },
                "source": "https://www.fortworthtexas.gov/departments/fire",
                "confidence": "high",
                "valid_from": "1873-01-01"
            },
            {
                "entity_type": "Department",
                "top_id": "dept-water-fort-worth",
                "properties": {
                    "entity_name": "Fort Worth Water Department",
                    "department_type": "utility",
                    "established_date": "1882-01-01",
                    "budget_fy2024": 450000000,
                    "employee_count": 600,
                    "director": "Chris Harder"
                },
                "source": "https://www.fortworthtexas.gov/departments/water",
                "confidence": "high",
                "valid_from": "1882-01-01"
            }
        ]
        
        relationships = [
            {
                "relationship_type": "PartOf",
                "source_entity": dept["top_id"],
                "target_entity": "city-fort-worth-tx",
                "properties": {
                    "oversight": "City Manager"
                },
                "source": dept["source"],
                "confidence": "high"
            }
            for dept in departments
        ]
        
        return {
            "entities": departments,
            "relationships": relationships
        }
    
    def create_legal_documents_data(self) -> Dict[str, Any]:
        """Create initial legal documents data."""
        documents = [
            {
                "entity_type": "Charter",
                "top_id": "charter-fort-worth-1924",
                "properties": {
                    "entity_name": "Fort Worth City Charter",
                    "adopted_date": "1924-01-01",
                    "last_amended": "2021-05-01",
                    "document_url": "https://www.fortworthtexas.gov/files/assets/public/city-secretary/documents/city-charter.pdf",
                    "amendment_count": 150
                },
                "source": "https://www.fortworthtexas.gov/government/city-charter",
                "confidence": "high",
                "valid_from": "1924-01-01"
            },
            {
                "entity_type": "Ordinance",
                "top_id": "ord-24-12345-fort-worth",
                "properties": {
                    "entity_name": "FY 2024 Annual Budget Ordinance",
                    "ordinance_number": "24-12345",
                    "adopted_date": "2023-09-19",
                    "effective_date": "2023-10-01",
                    "subject": "Annual Budget",
                    "fiscal_impact": 2100000000
                },
                "source": "https://www.fortworthtexas.gov/government/ordinances",
                "confidence": "high",
                "valid_from": "2023-10-01"
            }
        ]
        
        return {
            "entities": documents,
            "relationships": []
        }
    
    def create_bulk_episodes(self) -> List[RawEpisode]:
        """Create bulk episodes for initial data load."""
        episodes = []
        
        # City government structure
        city_data = self.create_fort_worth_city_data()
        episodes.append(RawEpisode(
            name="Fort Worth City Government Structure",
            content=json.dumps(city_data),
            source=EpisodeType.json,
            source_description="Texas Ontology Protocol - Initial City Data",
            reference_time=self.reference_time
        ))
        
        # City council data
        council_data = self.create_city_council_data()
        episodes.append(RawEpisode(
            name="Fort Worth City Council Districts and Members",
            content=json.dumps(council_data),
            source=EpisodeType.json,
            source_description="Texas Ontology Protocol - Council Data",
            reference_time=self.reference_time
        ))
        
        # Department data
        dept_data = self.create_department_data()
        episodes.append(RawEpisode(
            name="Fort Worth City Departments",
            content=json.dumps(dept_data),
            source=EpisodeType.json,
            source_description="Texas Ontology Protocol - Department Data",
            reference_time=self.reference_time
        ))
        
        # Legal documents
        legal_data = self.create_legal_documents_data()
        episodes.append(RawEpisode(
            name="Fort Worth Legal Documents",
            content=json.dumps(legal_data),
            source=EpisodeType.json,
            source_description="Texas Ontology Protocol - Legal Documents",
            reference_time=self.reference_time
        ))
        
        logger.info(f"Created {len(episodes)} initial data episodes")
        return episodes
    
    async def sync_initial_data(self):
        """Perform initial data synchronization."""
        logger.info("Starting initial Fort Worth data synchronization...")
        
        # Create bulk episodes
        episodes = self.create_bulk_episodes()
        
        # Add episodes in bulk for efficiency
        logger.info(f"Adding {len(episodes)} episodes to knowledge graph...")
        await self.graphiti.add_episode_bulk(
            episodes,
            entity_types=entity_types,
            edge_types=edge_types
        )
        
        logger.info("Initial data synchronization completed")
        
        # Build initial communities
        logger.info("Building initial communities...")
        await self.graphiti.build_communities()
        logger.info("Communities built successfully")


async def load_initial_data(graphiti):
    """Helper function to load initial Fort Worth data."""
    sync = InitialDataSync(graphiti)
    await sync.sync_initial_data()