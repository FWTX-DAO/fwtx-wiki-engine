"""
Data loader for Fort Worth municipal data.

This module uses AI agents to process raw data files and convert them 
to TOP-compliant structured entities.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from graphiti_core.nodes import EpisodeType
from graphiti_core.utils.bulk_utils import RawEpisode

from src.services.agent.researcher import FortWorthResearchWorkflow
from src.config import settings

logger = logging.getLogger(__name__)


class DataLoader:
    """Loads Fort Worth data from local files using AI processing."""
    
    def __init__(self, graphiti):
        self.graphiti = graphiti
        self.data_dir = Path(settings.BASE_DIR) / "data"
        self.workflow = FortWorthResearchWorkflow(graphiti)
        
    def glob_data_files(self, pattern: str) -> List[Path]:
        """Get all files matching pattern in data directory."""
        return list(self.data_dir.glob(pattern))
    
    async def process_data_files(self) -> List[RawEpisode]:
        """Process all data files using AI agents."""
        episodes = []
        
        # Define research tasks for each data file type
        research_tasks = []
        
        # Process governance.md
        governance_file = self.data_dir / "governance.md"
        if governance_file.exists():
            content = governance_file.read_text()
            research_tasks.append({
                "name": "Process Governance Structure",
                "config": {
                    "data_content": content,
                    "data_needed": [
                        "Extract all city leadership positions (Mayor, City Manager, Assistant City Managers)",
                        "Extract all council members and their districts",
                        "Extract department heads and organizational structure",
                        "Extract leadership transitions and dates",
                        "Create temporal relationships showing succession (e.g., David Cooke -> Jay Chapa)"
                    ],
                    "instructions": f"""
Process this governance document and extract all entities and relationships following TOP structure.
Pay special attention to:
- Jesus "Jay" Chapa becoming City Manager on January 28, 2025
- David Cooke retiring in February 2025 after 10+ years
- All council members and their districts
- All department heads and Assistant City Managers

Content to process:
{content}

Return structured JSON with entities and relationships following the Texas Ontology Protocol.
"""
                }
            })
        
        # Process fwtx.json
        json_file = self.data_dir / "fwtx.json"
        if json_file.exists():
            with open(json_file) as f:
                json_data = json.load(f)
            research_tasks.append({
                "name": "Process City Services Data",
                "config": {
                    "data_content": json.dumps(json_data, indent=2),
                    "data_needed": [
                        "Extract all city services and their details",
                        "Extract all department information",
                        "Extract URLs and contact information",
                        "Create relationships between services and departments"
                    ],
                    "instructions": f"""
Process this JSON file containing Fort Worth city services and extract entities following TOP structure.

Content to process:
{json.dumps(json_data, indent=2)}

Return structured JSON with entities and relationships.
"""
                }
            })
        
        # Process PDFs if needed (requires PDF processing in research agent)
        pdf_files = self.glob_data_files("*.pdf")
        for pdf_path in pdf_files:
            logger.info(f"Found PDF: {pdf_path.name} - AI agents will need web access to process PDFs")
            research_tasks.append({
                "name": f"Research {pdf_path.stem} Information",
                "config": {
                    "search_queries": [
                        f"Fort Worth {pdf_path.stem.replace('-', ' ').replace('_', ' ')} 2024 2025",
                        f"Fort Worth Texas {pdf_path.stem.replace('fwtx', '').replace('-', ' ')} official"
                    ],
                    "data_needed": [
                        f"Information related to {pdf_path.stem}",
                        "Official sources and documents",
                        "Current status and updates"
                    ]
                }
            })
        
        # Process all tasks with AI agents
        if research_tasks:
            logger.info(f"Processing {len(research_tasks)} data files with AI agents")
            research_episodes = await self.workflow.research_all_tasks(research_tasks)
            episodes.extend(research_episodes)
            logger.info(f"AI agents created {len(research_episodes)} episodes from data files")
        
        return episodes
    
    async def sync_to_graphiti(self):
        """Sync all data to Graphiti using AI processing."""
        logger.info("Starting AI-powered data sync...")
        
        episodes = await self.process_data_files()
        
        if episodes:
            await self.graphiti.add_episode_bulk(episodes)
            logger.info(f"Successfully synced {len(episodes)} episodes to Graphiti")
            
            # Build communities
            logger.info("Building communities...")
            await self.graphiti.build_communities()
            logger.info("Community building completed")
        else:
            logger.warning("No episodes created for sync")


# Convenience function for compatibility
async def load_and_sync_all_data(graphiti):
    """Load and sync all Fort Worth data using AI processing."""
    loader = DataLoader(graphiti)
    await loader.sync_to_graphiti()