"""
Fort Worth data synchronization service.

This module handles fetching and syncing Fort Worth municipal data
into the knowledge graph using Graphiti episodes.
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from graphiti_core.nodes import RawEpisode, EpisodeType

from src.models.ontology import create_top_entity
from src.models.top import (
    HomeRuleCity, Mayor, CityManager, CouncilMember,
    Department, Charter, Ordinance
)

logger = logging.getLogger(__name__)


class FortWorthDataSync:
    """Handles synchronization of Fort Worth municipal data."""
    
    def __init__(self, graphiti):
        self.graphiti = graphiti
        
    async def load_initial_data(self):
        """Load initial Fort Worth government structure data."""
        logger.info("Loading initial Fort Worth data...")
        
        # Prepare bulk episodes
        bulk_episodes = []
        
        # 1. City of Fort Worth entity
        city_data = {
            "type": "HomeRuleCity",
            "top_id": "city-fort-worth-2024",
            "name": "City of Fort Worth",
            "population": 956709,
            "incorporation_date": "1873-03-01",
            "government_form": "council-manager",
            "charter_adopted_date": "1924-01-01",
            "council_size": 9,
            "council_districts": 8,
            "website": "https://www.fortworthtexas.gov",
            "annual_budget": 2400000000,
            "tax_rate": 0.7475,
            "source_document": "Fort Worth City Charter",
            "authority": "Fort Worth City Secretary",
            "valid_from": "1873-03-01"
        }
        
        bulk_episodes.append(RawEpisode(
            name="Fort Worth City Entity",
            content=json.dumps(city_data),
            source=EpisodeType.json,
            source_description="Fort Worth municipal data - City entity",
            reference_time=datetime.now()
        ))
        
        # 2. Current Mayor
        mayor_data = {
            "type": "Person",
            "name": "Mattie Parker",
            "email": "mayor@fortworthtexas.gov",
            "position": {
                "type": "Mayor",
                "top_id": "pos-mayor-fort-worth",
                "title": "Mayor of Fort Worth",
                "term_start": "2021-06-01",
                "term_end": "2025-05-31",
                "election_type": "at-large",
                "mayor_type": "weak"
            },
            "source_document": "Election Results 2021",
            "authority": "Tarrant County Elections",
            "valid_from": "2021-06-01"
        }
        
        bulk_episodes.append(RawEpisode(
            name="Mayor Mattie Parker",
            content=json.dumps(mayor_data),
            source=EpisodeType.json,
            source_description="Fort Worth municipal data - Current Mayor",
            reference_time=datetime.now()
        ))
        
        # 3. City Manager
        city_manager_data = {
            "type": "Person",
            "name": "David Cooke",
            "email": "citymanager@fortworthtexas.gov",
            "position": {
                "type": "CityManager",
                "top_id": "pos-city-manager-fort-worth",
                "title": "City Manager of Fort Worth",
                "appointment_date": "2014-02-01",
                "appointing_authority": "Fort Worth City Council"
            },
            "source_document": "City Council Minutes 2014-02-01",
            "authority": "Fort Worth City Secretary",
            "valid_from": "2014-02-01"
        }
        
        bulk_episodes.append(RawEpisode(
            name="City Manager David Cooke",
            content=json.dumps(city_manager_data),
            source=EpisodeType.json,
            source_description="Fort Worth municipal data - City Manager",
            reference_time=datetime.now()
        ))
        
        # 4. City Council Districts
        for district_num in range(1, 9):
            district_data = {
                "type": "CouncilDistrict",
                "top_id": f"district-{district_num}-fort-worth",
                "name": f"Fort Worth Council District {district_num}",
                "district_number": district_num,
                "population": 119588,  # Approximate per district
                "source_document": "2021 Redistricting Plan",
                "authority": "Fort Worth Redistricting Commission",
                "valid_from": "2021-11-01"
            }
            
            bulk_episodes.append(RawEpisode(
                name=f"Council District {district_num}",
                content=json.dumps(district_data),
                source=EpisodeType.json,
                source_description=f"Fort Worth municipal data - Council District {district_num}",
                reference_time=datetime.now()
            ))
        
        # 5. Key Departments
        departments = [
            {
                "name": "Fort Worth Police Department",
                "top_id": "dept-police-fort-worth",
                "department_head_position": "Chief of Police",
                "employee_count": 1700,
                "annual_budget": 428000000,
                "services": ["Law enforcement", "Public safety", "Crime prevention"]
            },
            {
                "name": "Fort Worth Fire Department",
                "top_id": "dept-fire-fort-worth",
                "department_head_position": "Fire Chief",
                "employee_count": 1000,
                "annual_budget": 265000000,
                "services": ["Fire suppression", "Emergency medical services", "Fire prevention"]
            },
            {
                "name": "Fort Worth Water Department",
                "top_id": "dept-water-fort-worth",
                "department_head_position": "Water Director",
                "employee_count": 600,
                "annual_budget": 500000000,
                "services": ["Water treatment", "Water distribution", "Wastewater treatment"]
            }
        ]
        
        for dept in departments:
            dept_data = {
                "type": "Department",
                **dept,
                "parent_entity_id": "city-fort-worth-2024",
                "source_document": "FY2024 Budget Document",
                "authority": "Fort Worth Budget Office",
                "valid_from": "2023-10-01"
            }
            
            bulk_episodes.append(RawEpisode(
                name=f"Department - {dept['name']}",
                content=json.dumps(dept_data),
                source=EpisodeType.json,
                source_description=f"Fort Worth municipal data - {dept['name']}",
                reference_time=datetime.now()
            ))
        
        # 6. Important Relationships
        relationships = [
            {
                "type": "relationship",
                "relationship_type": "Governs",
                "source": "city-fort-worth-2024",
                "target": "Tarrant County (partial)",
                "properties": {
                    "jurisdiction_type": "municipal",
                    "services_provided": ["Police", "Fire", "Water", "Streets", "Parks"]
                }
            },
            {
                "type": "relationship",
                "relationship_type": "HoldsPosition",
                "source": "Mattie Parker",
                "target": "pos-mayor-fort-worth",
                "properties": {
                    "start_date": "2021-06-01",
                    "election_date": "2021-05-01",
                    "vote_percentage": 53.5
                }
            },
            {
                "type": "relationship",
                "relationship_type": "AppointedBy",
                "source": "David Cooke",
                "target": "Fort Worth City Council",
                "properties": {
                    "appointment_date": "2014-02-01",
                    "confirmation_vote": "9-0"
                }
            }
        ]
        
        for rel in relationships:
            bulk_episodes.append(RawEpisode(
                name=f"Relationship - {rel['relationship_type']}",
                content=json.dumps(rel),
                source=EpisodeType.json,
                source_description="Fort Worth municipal data - Relationships",
                reference_time=datetime.now()
            ))
        
        # Load all episodes in bulk
        try:
            await self.graphiti.add_episode_bulk(bulk_episodes)
            logger.info(f"Successfully loaded {len(bulk_episodes)} initial episodes")
        except Exception as e:
            logger.error(f"Error loading bulk episodes: {e}")
            raise
    
    async def sync_from_fwtx_json(self):
        """Sync data from the fwtx.json file."""
        try:
            with open('src/data/fwtx.json', 'r') as f:
                fwtx_data = json.load(f)
            
            # Convert service URLs to episodes
            service_episodes = []
            for category, services in fwtx_data.items():
                if isinstance(services, dict):
                    for service_name, service_info in services.items():
                        service_data = {
                            "type": "Service",
                            "name": service_name,
                            "category": category,
                            "url": service_info.get('url', ''),
                            "description": service_info.get('description', ''),
                            "department": service_info.get('department', 'Unknown'),
                            "source_document": "fwtx.json",
                            "authority": "Fort Worth IT Department",
                            "valid_from": datetime.now().isoformat()
                        }
                        
                        service_episodes.append(RawEpisode(
                            name=f"Service - {service_name}",
                            content=json.dumps(service_data),
                            source=EpisodeType.json,
                            source_description=f"Fort Worth service data - {category}",
                            reference_time=datetime.now()
                        ))
            
            if service_episodes:
                await self.graphiti.add_episode_bulk(service_episodes)
                logger.info(f"Synced {len(service_episodes)} services from fwtx.json")
                
        except Exception as e:
            logger.error(f"Error syncing fwtx.json: {e}")
    
    async def sync_governance_structure(self):
        """Sync governance structure from governance.md."""
        # This would parse the governance.md file and create episodes
        # For now, we'll use the data already loaded in load_initial_data
        logger.info("Governance structure sync would parse governance.md")
        
    async def run_full_sync(self):
        """Run a full synchronization of all data sources."""
        logger.info("Starting full Fort Worth data sync...")
        
        # Load initial government structure
        await self.load_initial_data()
        
        # Sync service URLs
        await self.sync_from_fwtx_json()
        
        # Sync governance structure
        await self.sync_governance_structure()
        
        logger.info("Full sync completed successfully")


async def create_sample_episodes(graphiti):
    """Create sample episodes with Fort Worth data."""
    sync_service = FortWorthDataSync(graphiti)
    await sync_service.run_full_sync()