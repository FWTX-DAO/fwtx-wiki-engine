"""
Fort Worth data synchronization service.

This module handles fetching and syncing Fort Worth municipal data
into the knowledge graph using live web searches and AI agents.
"""

import json
import logging
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from graphiti_core.nodes import EpisodeType
from graphiti_core.utils.bulk_utils import RawEpisode

logger = logging.getLogger(__name__)


class FortWorthDataSync:
    """Handles synchronization of Fort Worth municipal data using live data sources."""
    
    def __init__(self, graphiti):
        self.graphiti = graphiti
        self.base_urls = {
            "city": "https://www.fortworthtexas.gov",
            "council": "https://www.fortworthtexas.gov/government/city-council",
            "departments": "https://www.fortworthtexas.gov/departments",
            "data_portal": "https://data.fortworthtexas.gov"
        }
        
    async def fetch_current_mayor(self) -> Optional[Dict[str, Any]]:
        """Fetch current mayor information from web search."""
        logger.info("Fetching current Fort Worth mayor information...")
        
        search_queries = [
            "Fort Worth Texas current mayor 2024",
            "Mayor Mattie Parker Fort Worth contact information",
            "Fort Worth mayor office city hall"
        ]
        
        # This would use WebSearch or WebFetch tools to get live data
        # For now, returning structured format for what would be fetched
        return {
            "search_query": search_queries[0],
            "fetch_url": f"{self.base_urls['city']}/government/mayor",
            "data_needed": [
                "current_mayor_name",
                "term_start_date",
                "term_end_date",
                "contact_information",
                "biography",
                "initiatives"
            ]
        }
    
    async def fetch_city_council_members(self) -> List[Dict[str, Any]]:
        """Fetch current city council members from web search."""
        logger.info("Fetching Fort Worth city council members...")
        
        search_queries = [
            "Fort Worth city council members 2024 districts",
            "Fort Worth Texas council districts map representatives",
            "Fort Worth city council contact information"
        ]
        
        return {
            "search_queries": search_queries,
            "fetch_url": self.base_urls['council'],
            "data_needed": [
                "council_member_names",
                "district_numbers",
                "contact_information",
                "committee_assignments",
                "term_information"
            ]
        }
    
    async def fetch_city_departments(self) -> List[Dict[str, Any]]:
        """Fetch city department information from web search."""
        logger.info("Fetching Fort Worth city departments...")
        
        search_queries = [
            "Fort Worth city departments directory 2024",
            "Fort Worth Texas government departments services",
            "Fort Worth department heads contact information"
        ]
        
        return {
            "search_queries": search_queries,
            "fetch_url": self.base_urls['departments'],
            "data_needed": [
                "department_names",
                "department_heads",
                "services_provided",
                "contact_information",
                "locations"
            ]
        }
    
    async def fetch_city_data(self) -> Dict[str, Any]:
        """Fetch general city information from web search."""
        logger.info("Fetching Fort Worth city data...")
        
        search_queries = [
            "Fort Worth Texas population 2024 census",
            "Fort Worth city budget fiscal year 2024",
            "Fort Worth Texas government structure council-manager",
            "Fort Worth city charter home rule"
        ]
        
        return {
            "search_queries": search_queries,
            "data_portal_url": self.base_urls['data_portal'],
            "data_needed": [
                "population",
                "annual_budget",
                "tax_rate",
                "incorporation_date",
                "government_form",
                "city_services"
            ]
        }
    
    async def fetch_city_services(self) -> List[Dict[str, Any]]:
        """Fetch city services information from web search."""
        logger.info("Fetching Fort Worth city services...")
        
        service_categories = [
            "utilities water electric gas",
            "public safety police fire emergency",
            "development planning zoning permits",
            "transportation streets parking transit",
            "parks recreation libraries community"
        ]
        
        search_queries = []
        for category in service_categories:
            search_queries.append(f"Fort Worth Texas {category} services 2024")
        
        return {
            "search_queries": search_queries,
            "categories": service_categories,
            "data_needed": [
                "service_name",
                "service_url",
                "department_responsible",
                "contact_information",
                "hours_of_operation"
            ]
        }
    
    async def fetch_governance_structure(self) -> Dict[str, Any]:
        """Fetch governance structure from web search."""
        logger.info("Fetching Fort Worth governance structure...")
        
        search_queries = [
            "Fort Worth Texas council-manager government structure",
            "Fort Worth city charter home rule municipality",
            "Fort Worth Texas government organizational chart 2024",
            "Fort Worth city council committees boards commissions"
        ]
        
        return {
            "search_queries": search_queries,
            "data_needed": [
                "government_type",
                "charter_information",
                "organizational_structure",
                "committees_and_boards",
                "decision_making_process"
            ]
        }
        
    async def create_search_episode(self, search_config: Dict[str, Any], episode_name: str) -> RawEpisode:
        """Create an episode from search configuration for AI agent processing."""
        return RawEpisode(
            name=episode_name,
            content=json.dumps(search_config),
            source=EpisodeType.text,
            source_description=f"Web search configuration for {episode_name}",
            reference_time=datetime.now()
        )
    
    async def run_live_data_fetch(self) -> List[Dict[str, Any]]:
        """Fetch live data from Fort Worth sources."""
        logger.info("Starting live Fort Worth data fetch...")
        
        fetch_tasks = []
        
        # Fetch all data categories
        fetch_tasks.append({
            "name": "City Information",
            "config": await self.fetch_city_data()
        })
        
        fetch_tasks.append({
            "name": "Current Mayor",
            "config": await self.fetch_current_mayor()
        })
        
        fetch_tasks.append({
            "name": "City Council Members",
            "config": await self.fetch_city_council_members()
        })
        
        fetch_tasks.append({
            "name": "City Departments",
            "config": await self.fetch_city_departments()
        })
        
        fetch_tasks.append({
            "name": "City Services",
            "config": await self.fetch_city_services()
        })
        
        fetch_tasks.append({
            "name": "Governance Structure",
            "config": await self.fetch_governance_structure()
        })
        
        logger.info(f"Prepared {len(fetch_tasks)} data fetch tasks")
        return fetch_tasks


async def initialize_live_research(graphiti):
    """Initialize live research tasks for Fort Worth data."""
    from src.services.agent.researcher import FortWorthResearchWorkflow
    
    sync_service = FortWorthDataSync(graphiti)
    research_workflow = FortWorthResearchWorkflow(graphiti)
    
    logger.info("Initializing live Fort Worth data research...")
    
    # Get initial research tasks
    fetch_tasks = await sync_service.run_live_data_fetch()
    
    # Log the tasks that will be researched
    logger.info(f"Prepared {len(fetch_tasks)} research tasks:")
    for task in fetch_tasks:
        logger.info(f"  - {task['name']}")
    
    # Create initial research episodes using the workflow
    initial_episodes = await research_workflow.research_all_tasks(fetch_tasks)
    
    if initial_episodes:
        await graphiti.add_episode_bulk(initial_episodes)
        logger.info(f"Created {len(initial_episodes)} initial research task episodes")
    
    return fetch_tasks