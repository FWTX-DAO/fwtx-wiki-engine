"""
Data loader for synchronizing Fort Worth data from local files and AI research.

This module provides utilities to load data from various sources:
- JSON files in src/data/
- PDF documents (extracted text)
- Markdown files
- AI-researched data via the researcher agent
"""

import json
import logging
import glob
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import PyPDF2

from graphiti_core.nodes import EpisodeType
from graphiti_core.utils.bulk_utils import RawEpisode

from src.services.agent.researcher import FortWorthResearchWorkflow
from src.models.ontology import entity_types, edge_types, edge_type_map
from src.config import settings

logger = logging.getLogger(__name__)


class DataLoader:
    """Handles loading data from multiple sources for Fort Worth knowledge graph."""
    
    def __init__(self, graphiti):
        self.graphiti = graphiti
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.workflow = FortWorthResearchWorkflow(graphiti)
        
    def glob_data_files(self, pattern: str = "*") -> List[Path]:
        """
        Find all data files matching a pattern in the data directory.
        
        Args:
            pattern: Glob pattern to match files (e.g., "*.json", "*.pdf")
            
        Returns:
            List of Path objects for matching files
        """
        search_path = self.data_dir / pattern
        files = list(Path(self.data_dir).glob(pattern))
        logger.info(f"Found {len(files)} files matching pattern '{pattern}' in {self.data_dir}")
        return sorted(files)
    
    def load_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Load and parse a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded JSON data from {file_path}")
                return data
        except Exception as e:
            logger.error(f"Error loading JSON file {file_path}: {e}")
            return {}
    
    def load_markdown_file(self, file_path: Path) -> str:
        """Load content from a Markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.info(f"Loaded Markdown content from {file_path} ({len(content)} chars)")
                return content
        except Exception as e:
            logger.error(f"Error loading Markdown file {file_path}: {e}")
            return ""
    
    def extract_pdf_text(self, file_path: Path) -> str:
        """Extract text content from a PDF file."""
        try:
            text_parts = []
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        text_parts.append(text)
                
                full_text = "\n".join(text_parts)
                logger.info(f"Extracted {len(full_text)} chars from {num_pages} pages in {file_path}")
                return full_text
        except Exception as e:
            logger.error(f"Error extracting PDF text from {file_path}: {e}")
            return ""
    
    def create_fwtx_services_episodes(self) -> List[RawEpisode]:
        """Create episodes from fwtx.json service directory."""
        episodes = []
        fwtx_path = self.data_dir / "fwtx.json"
        
        if not fwtx_path.exists():
            logger.warning(f"fwtx.json not found at {fwtx_path}")
            return episodes
        
        data = self.load_json_file(fwtx_path)
        
        # Extract key service categories
        if "fort_worth_city_services" in data:
            services = data["fort_worth_city_services"]
            
            # Create episode for main city services
            episode_content = {
                "entities": [],
                "relationships": []
            }
            
            # Extract departments and services
            departments_data = []
            for category, details in services.items():
                if isinstance(details, dict) and "description" in details:
                    dept_name = category.replace("_", " ").title()
                    departments_data.append({
                        "category": category,
                        "name": dept_name,
                        "details": details
                    })
            
            # Create structured episode content
            episode_content["description"] = "Fort Worth city services extracted from service directory"
            episode_content["departments"] = departments_data
            episode_content["source"] = "fwtx.json service directory"
            
            episodes.append(RawEpisode(
                name="Fort Worth City Services Directory",
                content=json.dumps(episode_content),
                source=EpisodeType.json,
                source_description="Local data file - Fort Worth service directory",
                reference_time=datetime.now()
            ))
        
        # Extract 311 services
        if "fort_worth_311_services" in data:
            services_311 = data["fort_worth_311_services"]
            
            episode_content = {
                "service_type": "311 Customer Care",
                "contact_methods": services_311.get("service_request_methods", {}),
                "service_categories": services_311.get("service_categories", {}),
                "mobile_app": services_311.get("myfw_mobile_app", {}),
                "source": "fwtx.json 311 services"
            }
            
            episodes.append(RawEpisode(
                name="Fort Worth 311 Services",
                content=json.dumps(episode_content),
                source=EpisodeType.json,
                source_description="Local data file - 311 service information",
                reference_time=datetime.now()
            ))
        
        logger.info(f"Created {len(episodes)} episodes from fwtx.json")
        return episodes
    
    def create_governance_episodes(self) -> List[RawEpisode]:
        """Create episodes from governance.md file."""
        episodes = []
        governance_path = self.data_dir / "governance.md"
        
        if not governance_path.exists():
            logger.warning(f"governance.md not found at {governance_path}")
            return episodes
        
        content = self.load_markdown_file(governance_path)
        
        # Create episode for governance structure
        episodes.append(RawEpisode(
            name="Fort Worth Governance Structure",
            content=content,
            source=EpisodeType.text,
            source_description="Local data file - governance documentation",
            reference_time=datetime.now()
        ))
        
        return episodes
    
    def create_pdf_episodes(self) -> List[RawEpisode]:
        """Create episodes from PDF files in data directory."""
        episodes = []
        pdf_files = self.glob_data_files("*.pdf")
        
        for pdf_path in pdf_files:
            logger.info(f"Processing PDF: {pdf_path.name}")
            
            # Extract text from PDF
            pdf_text = self.extract_pdf_text(pdf_path)
            
            if pdf_text:
                # Determine episode name based on filename
                if "charter" in pdf_path.name.lower():
                    episode_name = "Fort Worth City Charter"
                    description = "Fort Worth City Charter document"
                elif "elected" in pdf_path.name.lower():
                    episode_name = "Fort Worth Elected Officials"
                    description = "Elected officials documentation"
                else:
                    episode_name = f"Document: {pdf_path.stem}"
                    description = f"PDF document: {pdf_path.name}"
                
                episodes.append(RawEpisode(
                    name=episode_name,
                    content=pdf_text,
                    source=EpisodeType.text,
                    source_description=f"Local PDF file - {description}",
                    reference_time=datetime.now()
                ))
        
        logger.info(f"Created {len(episodes)} episodes from PDF files")
        return episodes
    
    async def create_researched_episodes(self, research_tasks: List[Dict[str, Any]]) -> List[RawEpisode]:
        """
        Create episodes from AI-researched data.
        
        Args:
            research_tasks: List of research task configurations
            
        Returns:
            List of episodes from research results
        """
        logger.info(f"Starting AI research for {len(research_tasks)} tasks")
        
        # Use the workflow to research all tasks
        episodes = await self.workflow.research_all_tasks(research_tasks)
        
        logger.info(f"Created {len(episodes)} episodes from AI research")
        return episodes
    
    def create_structured_entities(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw data into TOP-compliant structured entities.
        
        Args:
            raw_data: Raw data dictionary
            
        Returns:
            Dictionary with entities and relationships arrays
        """
        entities = []
        relationships = []
        
        # Process Fort Worth city services data
        if "fort_worth_city_services" in raw_data:
            services = raw_data["fort_worth_city_services"]
            
            # Process utility services
            if "utilities" in services:
                utilities = services["utilities"]
                if "water_services" in utilities:
                    entities.append({
                        "entity_type": "Department",
                        "top_id": "dept-water-fort-worth",
                        "properties": {
                            "entity_name": "Fort Worth Water Department",
                            "department_type": "utility",
                            "contact": utilities["water_services"].get("contact"),
                            "service_hours": utilities["water_services"].get("service_hours"),
                            "services": utilities["water_services"].get("online_services", [])
                        },
                        "source": "fwtx.json",
                        "confidence": "high",
                        "valid_from": datetime.now().isoformat()
                    })
            
            # Process code compliance
            if "code_compliance" in services:
                code = services["code_compliance"]
                entities.append({
                    "entity_type": "Department",
                    "top_id": "dept-code-compliance-fort-worth",
                    "properties": {
                        "entity_name": "Fort Worth Code Compliance Department",
                        "department_type": "regulatory",
                        "description": code.get("description"),
                        "services": code.get("services", [])
                    },
                    "source": "fwtx.json",
                    "confidence": "high",
                    "valid_from": datetime.now().isoformat()
                })
        
        # Add relationships
        for entity in entities:
            if entity["entity_type"] == "Department":
                relationships.append({
                    "relationship_type": "PartOf",
                    "source_entity": entity["top_id"],
                    "target_entity": "city-fort-worth-tx",
                    "properties": {
                        "relationship_type": "administrative"
                    },
                    "source": "fwtx.json",
                    "confidence": "high"
                })
        
        return {
            "entities": entities,
            "relationships": relationships
        }
    
    async def load_all_data(self) -> List[RawEpisode]:
        """
        Load data from all available sources.
        
        Returns:
            Combined list of episodes from all sources
        """
        all_episodes = []
        
        # Load from local JSON files
        logger.info("Loading data from JSON files...")
        all_episodes.extend(self.create_fwtx_services_episodes())
        
        # Load from governance markdown
        logger.info("Loading data from governance documentation...")
        all_episodes.extend(self.create_governance_episodes())
        
        # Load from PDF files
        logger.info("Loading data from PDF files...")
        all_episodes.extend(self.create_pdf_episodes())
        
        # Define research tasks for AI agent
        research_tasks = [
            {
                "name": "Current City Council Members",
                "config": {
                    "search_queries": [
                        "Fort Worth Texas city council members 2024",
                        "Fort Worth council districts representatives"
                    ],
                    "data_needed": [
                        "council_member_names",
                        "district_numbers",
                        "contact_information",
                        "committee_assignments"
                    ]
                }
            },
            {
                "name": "Recent Ordinances and Resolutions",
                "config": {
                    "search_queries": [
                        "Fort Worth city council ordinances 2024",
                        "Fort Worth resolutions passed 2024"
                    ],
                    "data_needed": [
                        "ordinance_numbers",
                        "resolution_titles",
                        "approval_dates",
                        "vote_records"
                    ],
                    "fetch_url": "https://www.fortworthtexas.gov/government/ordinances"
                }
            },
            {
                "name": "City Department Updates",
                "config": {
                    "search_queries": [
                        "Fort Worth department directors 2024",
                        "Fort Worth city departments budget"
                    ],
                    "data_needed": [
                        "department_heads",
                        "budget_allocations",
                        "employee_counts",
                        "major_initiatives"
                    ]
                }
            }
        ]
        
        # Load from AI research
        if settings.SYNC_USE_AI_AGENT:
            logger.info("Loading data from AI research...")
            researched_episodes = await self.create_researched_episodes(research_tasks)
            all_episodes.extend(researched_episodes)
        else:
            logger.info("AI research disabled in settings")
        
        logger.info(f"Total episodes loaded: {len(all_episodes)}")
        return all_episodes
    
    async def sync_to_graphiti(self, episodes: Optional[List[RawEpisode]] = None):
        """
        Synchronize episodes to the Graphiti knowledge graph.
        
        Args:
            episodes: Optional list of episodes to sync. If None, loads all data.
        """
        if episodes is None:
            episodes = await self.load_all_data()
        
        if not episodes:
            logger.warning("No episodes to sync")
            return
        
        logger.info(f"Syncing {len(episodes)} episodes to Graphiti...")
        
        # Add episodes in bulk
        await self.graphiti.add_episode_bulk(
            episodes,
            entity_types=entity_types,
            edge_types=edge_types
        )
        
        logger.info("Sync completed successfully")
        
        # Build communities after sync
        logger.info("Building communities...")
        await self.graphiti.build_communities()
        logger.info("Community building completed")


# Convenience function for standalone use
async def load_and_sync_all_data(graphiti):
    """Helper function to load and sync all available data."""
    loader = DataLoader(graphiti)
    await loader.sync_to_graphiti()