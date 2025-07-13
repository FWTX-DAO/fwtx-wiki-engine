#!/usr/bin/env python3
"""
Test the full TOP implementation for Fort Worth Wiki.

This script verifies that all components are properly integrated
and producing TOP-compliant data.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

from src.models.top.structured import (
    TOPEpisodeData,
    StructuredEntity,
    StructuredRelationship,
    MayorData,
    DepartmentData,
    CouncilMemberData
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_structured_models():
    """Test structured model creation and validation."""
    logger.info("=== Testing Structured Models ===")
    
    # Test MayorData
    try:
        mayor = MayorData(
            person_name="Mattie Parker",
            term_start="2021-06-01",
            term_end="2025-05-31",
            political_party="Republican",
            contact_email="mayor@fortworthtexas.gov"
        )
        mayor_entity = mayor.to_top_entity()
        logger.info(f"✓ MayorData: {mayor_entity.top_id}")
    except Exception as e:
        logger.error(f"✗ MayorData failed: {e}")
    
    # Test DepartmentData
    try:
        dept = DepartmentData(
            department_name="Fort Worth Police Department",
            department_type="public_safety",
            director_name="Neil Noakes",
            budget_amount=328000000,
            employee_count=1700
        )
        dept_entity = dept.to_top_entity("fwtx:dept:police")
        logger.info(f"✓ DepartmentData: {dept_entity.top_id}")
    except Exception as e:
        logger.error(f"✗ DepartmentData failed: {e}")
    
    # Test CouncilMemberData
    try:
        council = CouncilMemberData(
            person_name="Carlos Flores",
            district_number=1,
            term_start="2023-06-01",
            term_end="2025-05-31"
        )
        member, district, rel = council.to_top_entities()
        logger.info(f"✓ CouncilMemberData: {member.top_id} serves {district.top_id}")
    except Exception as e:
        logger.error(f"✗ CouncilMemberData failed: {e}")
    
    # Test TOPEpisodeData
    try:
        episode = TOPEpisodeData()
        episode.entities.append(mayor_entity)
        episode.entities.append(dept_entity)
        episode.relationships.append(StructuredRelationship(
            relationship_type="PartOf",
            source_entity=dept_entity.top_id,
            target_entity="fwtx:city:fort-worth",
            source="test",
            confidence="high"
        ))
        
        # Validate references
        missing = episode.validate_entity_references()
        if missing:
            logger.warning(f"  Missing entities: {missing}")
        else:
            logger.info("✓ TOPEpisodeData: All references valid")
            
        # Test JSON serialization
        json_str = episode.to_episode_content()
        parsed = json.loads(json_str)
        logger.info(f"✓ JSON serialization: {len(parsed['entities'])} entities, {len(parsed['relationships'])} relationships")
        
    except Exception as e:
        logger.error(f"✗ TOPEpisodeData failed: {e}")


async def test_data_loader():
    """Test the data loader with structured outputs."""
    logger.info("\n=== Testing Data Loader ===")
    
    from src.services.sync.data_loader import DataLoader
    
    # Mock graphiti for testing
    class MockGraphiti:
        async def add_episode_bulk(self, episodes):
            logger.info(f"  Mock: Would add {len(episodes)} episodes")
            return True
        
        async def build_communities(self):
            logger.info("  Mock: Would build communities")
            return True
    
    try:
        loader = DataLoader(MockGraphiti())
        
        # Test file globbing
        json_files = loader.glob_data_files("*.json")
        logger.info(f"✓ Found {len(json_files)} JSON files")
        
        pdf_files = loader.glob_data_files("*.pdf")
        logger.info(f"✓ Found {len(pdf_files)} PDF files")
        
        # Test structured entity creation
        raw_data = {"fort_worth_city_services": {"utilities": {"water_services": {}}}}
        structured = loader.create_structured_entities(raw_data)
        logger.info(f"✓ Created {len(structured['entities'])} entities from raw data")
        
    except Exception as e:
        logger.error(f"✗ Data loader test failed: {e}")


async def test_research_workflow():
    """Test the research workflow with structured outputs."""
    logger.info("\n=== Testing Research Workflow ===")
    
    from src.services.agent.researcher import FortWorthResearchWorkflow
    
    try:
        workflow = FortWorthResearchWorkflow()
        
        # Test prompt building
        task = {
            "name": "Test Mayor Research",
            "config": {
                "search_queries": ["Fort Worth mayor 2024"],
                "data_needed": ["name", "term_dates"]
            }
        }
        
        prompt = workflow._build_research_prompt(task)
        logger.info("✓ Research prompt built successfully")
        
        # Test result processing with structured data
        test_json = json.dumps({
            "entities": [{
                "entity_type": "Mayor",
                "top_id": "fwtx:mayor:test",
                "properties": {"entity_name": "Test Mayor"},
                "source": "test",
                "confidence": "high"
            }],
            "relationships": []
        })
        
        test_content = f"```json\n{test_json}\n```"
        episodes = workflow._process_research_results(test_content, "Test")
        logger.info(f"✓ Processed research results: {len(episodes)} episodes")
        
    except Exception as e:
        logger.error(f"✗ Research workflow test failed: {e}")


async def test_top_loader():
    """Test the TOP loader."""
    logger.info("\n=== Testing TOP Loader ===")
    
    from src.services.sync.top_loader import TOPDataLoader
    
    class MockGraphiti:
        episodes_added = 0
        
        async def add_episode_bulk(self, episodes):
            self.episodes_added += len(episodes)
            return True
        
        async def build_communities(self):
            return True
    
    try:
        mock_graphiti = MockGraphiti()
        loader = TOPDataLoader(mock_graphiti)
        
        # Test entity creation
        base_episode = await loader.create_base_entities()
        logger.info(f"✓ Base entities: {len(base_episode.entities)} entities, {len(base_episode.relationships)} relationships")
        
        gov_episode = await loader.create_government_structure()
        logger.info(f"✓ Government structure: {len(gov_episode.entities)} entities, {len(gov_episode.relationships)} relationships")
        
        council_episode = await loader.create_council_districts()
        logger.info(f"✓ Council districts: {len(council_episode.entities)} entities, {len(council_episode.relationships)} relationships")
        
        dept_episode = await loader.create_city_departments()
        logger.info(f"✓ Departments: {len(dept_episode.entities)} entities, {len(dept_episode.relationships)} relationships")
        
        legal_episode = await loader.create_legal_documents()
        logger.info(f"✓ Legal documents: {len(legal_episode.entities)} entities, {len(legal_episode.relationships)} relationships")
        
        # Validate all episodes
        all_episodes = [base_episode, gov_episode, council_episode, dept_episode, legal_episode]
        total_entities = sum(len(ep.entities) for ep in all_episodes)
        total_relationships = sum(len(ep.relationships) for ep in all_episodes)
        
        logger.info(f"\n✓ Total TOP data created:")
        logger.info(f"  - Entities: {total_entities}")
        logger.info(f"  - Relationships: {total_relationships}")
        
    except Exception as e:
        logger.error(f"✗ TOP loader test failed: {e}")


async def main():
    """Run all tests."""
    logger.info("=== Fort Worth Wiki TOP Implementation Test ===\n")
    
    # Test structured models
    await test_structured_models()
    
    # Test data loader
    await test_data_loader()
    
    # Test research workflow
    await test_research_workflow()
    
    # Test TOP loader
    await test_top_loader()
    
    logger.info("\n=== Test Summary ===")
    logger.info("All components have been tested for TOP compliance.")
    logger.info("Check the logs above for any errors or warnings.")


if __name__ == "__main__":
    asyncio.run(main())