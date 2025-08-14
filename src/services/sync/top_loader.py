"""
TOP-compliant data loader for Fort Worth municipal data.

This module uses AI research agents to dynamically fetch Fort Worth data
with full Texas Ontology Protocol compliance.
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
from src.services.agent.researcher import FortWorthResearchWorkflow

logger = logging.getLogger(__name__)


class TOPDataLoader:
    """Loads Fort Worth data with full TOP compliance using AI research."""
    
    def __init__(self, graphiti):
        self.graphiti = graphiti
        self.research_workflow = FortWorthResearchWorkflow(graphiti)
        
    async def get_research_tasks(self) -> List[Dict[str, Any]]:
        """Define research tasks for comprehensive Fort Worth data."""
        return [
            {
                "name": "Fort Worth City Structure",
                "config": {
                    "search_queries": [
                        "Fort Worth Texas city government structure 2024 2025",
                        "Fort Worth home rule charter council-manager",
                        "Fort Worth population area demographics 2024"
                    ],
                    "data_needed": [
                        "city_type",
                        "incorporation_date",
                        "charter_date",
                        "population",
                        "area_sq_miles",
                        "county",
                        "government_form"
                    ]
                }
            },
            {
                "name": "Current City Leadership",
                "config": {
                    "search_queries": [
                        "Fort Worth mayor Mattie Parker 2024 2025",
                        "Fort Worth city manager Jay Chapa 2025",
                        "Fort Worth city council members 2024 2025",
                        "Fort Worth city leadership changes 2025"
                    ],
                    "data_needed": [
                        "mayor_name",
                        "mayor_term_dates",
                        "city_manager_name",
                        "city_manager_appointment_date",
                        "council_members",
                        "leadership_transitions"
                    ]
                }
            },
            {
                "name": "City Departments",
                "config": {
                    "search_queries": [
                        "Fort Worth city departments 2024",
                        "Fort Worth police fire departments",
                        "Fort Worth water utilities code compliance",
                        "Fort Worth department directors 2024"
                    ],
                    "data_needed": [
                        "department_names",
                        "department_heads",
                        "department_types",
                        "budgets",
                        "employee_counts"
                    ]
                }
            },
            {
                "name": "Council Districts",
                "config": {
                    "search_queries": [
                        "Fort Worth city council districts 2024",
                        "Fort Worth council district boundaries population",
                        "Fort Worth council members by district 2024"
                    ],
                    "data_needed": [
                        "district_numbers",
                        "district_populations",
                        "council_member_names",
                        "district_boundaries"
                    ]
                }
            },
            {
                "name": "Legal Framework",
                "config": {
                    "search_queries": [
                        "Fort Worth city charter",
                        "Fort Worth home rule charter amendments",
                        "Fort Worth legal authority Texas Local Government Code"
                    ],
                    "data_needed": [
                        "charter_adoption_date",
                        "charter_amendments",
                        "legal_authority",
                        "home_rule_status"
                    ]
                }
            }
        ]
    
    async def load_all_top_data(self) -> List[RawEpisode]:
        """Load all Fort Worth data using AI research agents."""
        episodes = []
        
        try:
            # Add initial episode for schema
            await add_ontology_episode(self.graphiti, episode_type="government")
            
            # Get research tasks
            tasks = await self.get_research_tasks()
            
            # Research all tasks using AI agents
            logger.info("Starting AI research for Fort Worth data...")
            research_episodes = await self.research_workflow.research_all_tasks(tasks)
            
            if research_episodes:
                episodes.extend(research_episodes)
                logger.info(f"AI research generated {len(research_episodes)} episodes")
            else:
                logger.warning("No episodes generated from AI research")
            
        except Exception as e:
            logger.error(f"Error during AI research: {e}")
            raise
        
        return episodes
    
    async def sync_to_graphiti(self):
        """Sync all TOP data to Graphiti using AI research."""
        logger.info("Starting TOP-compliant Fort Worth data sync using AI research...")
        
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
    """Load Fort Worth data with full TOP compliance using AI research."""
    loader = TOPDataLoader(graphiti)
    await loader.sync_to_graphiti()