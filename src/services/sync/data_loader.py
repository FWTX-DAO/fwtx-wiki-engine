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
import re
import PyPDF2

from graphiti_core.nodes import EpisodeType
from graphiti_core.utils.bulk_utils import RawEpisode

from src.services.agent.researcher import FortWorthResearchWorkflow
from src.models.ontology import entity_types, edge_types, edge_type_map
from src.models.top.structured import TOPEpisodeData, StructuredEntity, StructuredRelationship
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
        
        # Create structured entities from raw data
        structured_data = self.create_structured_entities(data)
        
        # Create episode for Fort Worth entities
        if structured_data["entities"]:
            episodes.append(RawEpisode(
                name="Fort Worth City Structure and Departments",
                content=json.dumps(structured_data),
                source=EpisodeType.json,
                source_description="Local data file - Fort Worth service directory",
                reference_time=datetime.now()
            ))
        
        # Extract 311 services as separate episode
        if "fort_worth_311_services" in data:
            services_311 = data["fort_worth_311_services"]
            
            entities_311 = []
            relationships_311 = []
            
            # Create 311 department entity
            entities_311.append({
                "entity_type": "Department",
                "top_id": "fwtx:dept:311",
                "properties": {
                    "entity_name": "Fort Worth 311 Customer Care",
                    "department_type": "customer_service",
                    "description": "Single point of contact for city services",
                    "contact_methods": services_311.get("service_request_methods", {}),
                    "service_categories": list(services_311.get("service_categories", {}).keys()),
                    "mobile_app": services_311.get("myfw_mobile_app", {}).get("name"),
                    "parent_organization": "fwtx:city:fort-worth"
                },
                "source": "fwtx.json",
                "confidence": "high",
                "valid_from": datetime.now().isoformat()
            })
            
            relationships_311.append({
                "relationship_type": "PartOf",
                "source_entity": "fwtx:dept:311",
                "target_entity": "fwtx:city:fort-worth",
                "properties": {
                    "relationship_type": "administrative"
                },
                "source": "fwtx.json",
                "confidence": "high"
            })
            
            episode_content = {
                "entities": entities_311,
                "relationships": relationships_311
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
        
        # Process governance markdown to extract structured data
        structured_data = self.process_governance_markdown(content)
        
        if structured_data["entities"] or structured_data["relationships"]:
            episodes.append(RawEpisode(
                name="Fort Worth Governance Structure",
                content=json.dumps(structured_data),
                source=EpisodeType.json,
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
                structured_data = None
                
                # Process based on filename
                if "charter" in pdf_path.name.lower():
                    structured_data = self.process_charter_pdf(pdf_text)
                    episode_name = "Fort Worth City Charter"
                elif "elected" in pdf_path.name.lower():
                    structured_data = self.process_elected_officials_pdf(pdf_text)
                    episode_name = "Fort Worth Elected Officials"
                else:
                    episode_name = f"Document: {pdf_path.stem}"
                    # For other PDFs, just store as text
                    episodes.append(RawEpisode(
                        name=episode_name,
                        content=pdf_text,
                        source=EpisodeType.text,
                        source_description=f"Local PDF file - {pdf_path.name}",
                        reference_time=datetime.now()
                    ))
                    continue
                
                # Add structured episode if data was extracted
                if structured_data and (structured_data["entities"] or structured_data["relationships"]):
                    episodes.append(RawEpisode(
                        name=episode_name,
                        content=json.dumps(structured_data),
                        source=EpisodeType.json,
                        source_description=f"Local PDF file - {pdf_path.name}",
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
    
    def process_governance_markdown(self, content: str) -> Dict[str, Any]:
        """
        Extract structured data from governance markdown.
        
        Args:
            content: Markdown content
            
        Returns:
            Dictionary with entities and relationships
        """
        entities = []
        relationships = []
        
        # Extract mayor information
        mayor_match = re.search(r"Mayor:\s*([^\n]+)", content)
        if mayor_match:
            mayor_name = mayor_match.group(1).strip()
            mayor = {
                "entity_type": "Mayor",
                "top_id": "fwtx:mayor:current",
                "properties": {
                    "entity_name": f"Mayor {mayor_name}",
                    "person_name": mayor_name,
                    "term_start": "2021-06-01",  # Mattie Parker's term
                    "term_end": "2025-05-31",
                    "election_type": "at-large",
                    "political_party": "Republican"
                },
                "source": "governance.md",
                "confidence": "high",
                "valid_from": "2021-06-01"
            }
            entities.append(mayor)
            
            # Note: In TOP, the Mayor entity itself represents the person holding the position
            # No need for separate Person entity
        
        # Extract council districts
        district_pattern = re.compile(r"District\s+(\d+):\s*([^\n]+)")
        for match in district_pattern.finditer(content):
            district_num = match.group(1)
            member_name = match.group(2).strip()
            
            # Create district entity
            district = {
                "entity_type": "CouncilDistrict",
                "top_id": f"fwtx:district:{district_num}",
                "properties": {
                    "entity_name": f"Fort Worth Council District {district_num}",
                    "district_number": int(district_num),
                    "population": 95000,  # Approximate
                    "established_date": "2022-01-01"  # Last redistricting
                },
                "source": "governance.md",
                "confidence": "high",
                "valid_from": "2022-01-01"
            }
            entities.append(district)
            
            # Create council member
            council_member = {
                "entity_type": "CouncilMember",
                "top_id": f"fwtx:councilmember:district-{district_num}",
                "properties": {
                    "entity_name": f"Council Member {member_name}",
                    "person_name": member_name,
                    "district_number": int(district_num),
                    "term_start": "2023-06-01",
                    "term_end": "2025-05-31",
                    "election_type": "single-member-district"
                },
                "source": "governance.md",
                "confidence": "high",
                "valid_from": "2023-06-01"
            }
            entities.append(council_member)
            
            # Create relationships
            relationships.append({
                "relationship_type": "Serves",
                "source_entity": council_member["top_id"],
                "target_entity": district["top_id"],
                "properties": {"elected": "2023-05-06"},
                "source": "governance.md",
                "confidence": "high"
            })
            
            relationships.append({
                "relationship_type": "PartOf",
                "source_entity": district["top_id"],
                "target_entity": "fwtx:city:fort-worth",
                "properties": {"type": "administrative_division"},
                "source": "governance.md",
                "confidence": "high"
            })
        
        return {
            "entities": entities,
            "relationships": relationships
        }
    
    def process_charter_pdf(self, text: str) -> Dict[str, Any]:
        """
        Extract structured data from city charter PDF.
        
        Args:
            text: Extracted PDF text
            
        Returns:
            Dictionary with entities and relationships
        """
        entities = []
        relationships = []
        
        # Create charter entity
        charter = {
            "entity_type": "Charter",
            "top_id": "fwtx:charter:1924",
            "properties": {
                "entity_name": "Fort Worth City Charter",
                "document_number": "Charter-1924",
                "title": "Charter of the City of Fort Worth",
                "date_adopted": "1924-01-01",
                "effective_date": "1924-01-01",
                "adopted_by": "City of Fort Worth",
                "amendments": 150,  # Approximate from research
                "source_type": "pdf_extract"
            },
            "source": "fwtx-charter.pdf",
            "confidence": "high",
            "valid_from": "1924-01-01"
        }
        entities.append(charter)
        
        # Create relationship
        relationships.append({
            "relationship_type": "Governs",
            "source_entity": "fwtx:charter:1924",
            "target_entity": "fwtx:city:fort-worth",
            "properties": {
                "authority": "home-rule",
                "legal_basis": "Texas Local Government Code"
            },
            "source": "fwtx-charter.pdf",
            "confidence": "high"
        })
        
        # Extract articles if possible
        article_pattern = re.compile(r"ARTICLE\s+([IVX]+)\.\s*([^\n]+)")
        for match in article_pattern.finditer(text):
            article_num = match.group(1)
            article_title = match.group(2).strip()
            
            entities.append({
                "entity_type": "LegalDocument",
                "top_id": f"fwtx:charter:article-{article_num}",
                "properties": {
                    "entity_name": f"Article {article_num}: {article_title}",
                    "document_type": "charter_article",
                    "part_of": "fwtx:charter:1924"
                },
                "source": "fwtx-charter.pdf",
                "confidence": "medium"
            })
        
        return {
            "entities": entities,
            "relationships": relationships
        }
    
    def process_elected_officials_pdf(self, text: str) -> Dict[str, Any]:
        """
        Extract structured data from elected officials PDF.
        
        Args:
            text: Extracted PDF text
            
        Returns:
            Dictionary with entities and relationships
        """
        entities = []
        relationships = []
        
        # Look for patterns like "Mayor: Name" or "District X: Name"
        lines = text.split('\n')
        
        for line in lines:
            # Mayor pattern
            if match := re.match(r"Mayor[:\s]+(.+)", line, re.IGNORECASE):
                name = match.group(1).strip()
                if name and not any(x in name.lower() for x in ['vacant', 'tbd', 'none']):
                    logger.info(f"Found Mayor: {name}")
                    
                    mayor = {
                        "entity_type": "Mayor",
                        "top_id": "fwtx:mayor:current-pdf",
                        "properties": {
                            "entity_name": f"Mayor {name}",
                            "person_name": name,
                            "source_type": "pdf_extract"
                        },
                        "source": "elected_officials.pdf",
                        "confidence": "medium"
                    }
                    entities.append(mayor)
                    
            # Council member pattern
            if match := re.match(r"District\s+(\d+)[:\s]+(.+)", line, re.IGNORECASE):
                district = match.group(1)
                name = match.group(2).strip()
                if name and not any(x in name.lower() for x in ['vacant', 'tbd', 'none']):
                    logger.info(f"Found District {district} Council Member: {name}")
                    
                    council_member = {
                        "entity_type": "CouncilMember",
                        "top_id": f"fwtx:councilmember:district-{district}-pdf",
                        "properties": {
                            "entity_name": f"Council Member {name}",
                            "person_name": name,
                            "district_number": int(district),
                            "source_type": "pdf_extract"
                        },
                        "source": "elected_officials.pdf",
                        "confidence": "medium"
                    }
                    entities.append(council_member)
        
        return {
            "entities": entities,
            "relationships": relationships
        }

    def create_structured_entities(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw data into TOP-compliant structured entities.
        
        Args:
            raw_data: Raw data dictionary
            
        Returns:
            Dictionary with entities and relationships arrays
        """
        # Use structured models for validation
        episode_data = TOPEpisodeData()
        
        # Create Fort Worth city entity
        city = StructuredEntity(
            entity_type="HomeRuleCity",
            top_id="fwtx:city:fort-worth",
            properties={
                "entity_name": "City of Fort Worth",
                "population": 956709,
                "charter_adopted": "1924-01-01",
                "governmental_form": "council-manager",
                "incorporation_date": "1873-03-19",
                "website": "https://fortworthtexas.gov",
                "county": "Tarrant County",
                "state": "Texas"
            },
            source="fwtx.json",
            confidence="high",
            valid_from="1873-03-19"
        )
        episode_data.entities.append(city)
        
        # Process Fort Worth city services data
        if "fort_worth_city_services" in raw_data:
            services = raw_data["fort_worth_city_services"]
            
            # Process utility services
            if "utilities" in services:
                utilities = services["utilities"]
                if "water_services" in utilities:
                    water_dept = StructuredEntity(
                        entity_type="Department",
                        top_id="fwtx:dept:water",
                        properties={
                            "entity_name": "Fort Worth Water Department",
                            "department_type": "utility",
                            "contact": utilities["water_services"].get("contact"),
                            "service_hours": utilities["water_services"].get("service_hours"),
                            "services": utilities["water_services"].get("online_services", []),
                            "parent_organization": "fwtx:city:fort-worth"
                        },
                        source="fwtx.json",
                        confidence="high",
                        valid_from=datetime.now().isoformat()
                    )
                    episode_data.entities.append(water_dept)
            
            # Process code compliance
            if "code_compliance" in services:
                code = services["code_compliance"]
                entities.append({
                    "entity_type": "Department",
                    "top_id": "fwtx:dept:code-compliance",
                    "properties": {
                        "entity_name": "Fort Worth Code Compliance Department",
                        "department_type": "regulatory",
                        "description": code.get("description"),
                        "services": code.get("services", []),
                        "parent_organization": "fwtx:city:fort-worth"
                    },
                    "source": "fwtx.json",
                    "confidence": "high",
                    "valid_from": datetime.now().isoformat()
                })
            
            # Process public safety
            if "public_safety" in services:
                safety = services["public_safety"]
                if "police" in safety:
                    entities.append({
                        "entity_type": "Department",
                        "top_id": "fwtx:dept:police",
                        "properties": {
                            "entity_name": "Fort Worth Police Department",
                            "department_type": "public_safety",
                            "emergency_number": "911",
                            "non_emergency": safety["police"].get("non_emergency_number"),
                            "parent_organization": "fwtx:city:fort-worth"
                        },
                        "source": "fwtx.json",
                        "confidence": "high",
                        "valid_from": "1873-01-01"
                    })
                if "fire" in safety:
                    entities.append({
                        "entity_type": "Department",
                        "top_id": "fwtx:dept:fire",
                        "properties": {
                            "entity_name": "Fort Worth Fire Department",
                            "department_type": "public_safety",
                            "emergency_number": "911",
                            "stations": safety["fire"].get("stations", []),
                            "parent_organization": "fwtx:city:fort-worth"
                        },
                        "source": "fwtx.json",
                        "confidence": "high",
                        "valid_from": "1873-01-01"
                    })
        
        # Add relationships
        for entity in episode_data.entities:
            if entity.entity_type == "Department":
                rel = StructuredRelationship(
                    relationship_type="PartOf",
                    source_entity=entity.top_id,
                    target_entity="fwtx:city:fort-worth",
                    properties={
                        "relationship_type": "administrative"
                    },
                    source="fwtx.json",
                    confidence="high"
                )
                episode_data.relationships.append(rel)
        
        # Validate and return as dict
        missing = episode_data.validate_entity_references()
        if missing:
            logger.warning(f"Missing entity references in structured data: {missing}")
        
        return {
            "entities": [e.model_dump() for e in episode_data.entities],
            "relationships": [r.model_dump() for r in episode_data.relationships]
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