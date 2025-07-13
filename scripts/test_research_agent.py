#!/usr/bin/env python3
"""
Test the AI research agent to diagnose why it's not producing output.
"""

import asyncio
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Silence some noisy loggers
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

load_dotenv()


async def test_basic_agent():
    """Test basic agent functionality."""
    logger.info("=== Testing Basic Agent ===")
    
    try:
        from agno.agent import Agent
        from agno.models.openai import OpenAIChat
        from src.config import settings
        
        # Create simple agent
        agent = Agent(
            name="Test Agent",
            model=OpenAIChat(id=settings.OPENAI_MODEL),
            instructions=["You are a helpful assistant"]
        )
        
        # Test basic response
        response = agent.run("Say hello")
        logger.info(f"Agent response: {response.content}")
        
    except Exception as e:
        logger.error(f"Basic agent test failed: {e}", exc_info=True)


async def test_research_workflow():
    """Test the research workflow directly."""
    logger.info("\n=== Testing Research Workflow ===")
    
    try:
        from src.services.agent.researcher import FortWorthResearchWorkflow
        
        # Create workflow
        workflow = FortWorthResearchWorkflow()
        
        # Create simple test task
        test_task = {
            "name": "Test Mayor Research",
            "config": {
                "search_queries": ["Fort Worth mayor Mattie Parker 2024"],
                "data_needed": ["mayor_name", "term_dates"]
            }
        }
        
        logger.info(f"Running research task: {test_task['name']}")
        
        # Run the workflow
        responses = []
        for response in workflow.run(test_task):
            if response.content:
                logger.info(f"Got response: {response.content[:200]}...")
                responses.append(response.content)
        
        # Check session state
        episodes = workflow.session_state.get(f"{test_task['name']}_episodes", [])
        logger.info(f"Episodes created: {len(episodes)}")
        
        if not responses:
            logger.warning("No responses received from workflow")
        
        return responses
        
    except Exception as e:
        logger.error(f"Research workflow test failed: {e}", exc_info=True)
        return []


async def test_data_sync():
    """Test the Fort Worth data sync service."""
    logger.info("\n=== Testing Data Sync Service ===")
    
    try:
        from src.services.sync.fort_worth_data import FortWorthDataSync
        
        # Mock graphiti
        class MockGraphiti:
            pass
        
        sync = FortWorthDataSync(MockGraphiti())
        
        # Test task generation
        tasks = await sync.run_live_data_fetch()
        logger.info(f"Generated {len(tasks)} research tasks:")
        
        for task in tasks:
            logger.info(f"  - {task['name']}: {len(task['config'].get('search_queries', []))} queries")
        
        return tasks
        
    except Exception as e:
        logger.error(f"Data sync test failed: {e}", exc_info=True)
        return []


async def test_full_pipeline():
    """Test the full research pipeline."""
    logger.info("\n=== Testing Full Research Pipeline ===")
    
    try:
        from src.services.agent.researcher import FortWorthResearchWorkflow
        from src.services.sync.fort_worth_data import FortWorthDataSync
        
        # Create components
        class MockGraphiti:
            async def add_episode_bulk(self, episodes):
                logger.info(f"Mock: Would add {len(episodes)} episodes")
                return True
        
        mock_graphiti = MockGraphiti()
        sync_service = FortWorthDataSync(mock_graphiti)
        workflow = FortWorthResearchWorkflow(mock_graphiti)
        
        # Get tasks
        fetch_tasks = await sync_service.run_live_data_fetch()
        logger.info(f"Testing with {len(fetch_tasks)} tasks")
        
        # Test just the first task
        if fetch_tasks:
            task = fetch_tasks[0]
            logger.info(f"\nTesting task: {task['name']}")
            logger.info(f"Config: {task['config']}")
            
            # Run research
            responses = []
            for response in workflow.run(task):
                if response and response.content:
                    logger.info(f"Response received (length: {len(response.content)})")
                    responses.append(response.content)
            
            # Check for episodes
            episodes = workflow.session_state.get(f"{task['name']}_episodes", [])
            logger.info(f"Episodes created: {len(episodes)}")
            
            if episodes:
                for i, ep in enumerate(episodes[:2]):  # Show first 2
                    logger.info(f"Episode {i+1}: {ep.name}")
        
    except Exception as e:
        logger.error(f"Full pipeline test failed: {e}", exc_info=True)


async def check_api_keys():
    """Check if API keys are properly configured."""
    logger.info("\n=== Checking API Keys ===")
    
    from src.config import settings
    
    if settings.OPENAI_API_KEY:
        logger.info("✓ OpenAI API key is set")
        logger.info(f"  Model: {settings.OPENAI_MODEL}")
        logger.info(f"  Base URL: {settings.OPENAI_API_BASE}")
    else:
        logger.error("✗ OpenAI API key is NOT set")
    
    # Test OpenAI connection
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Simple test
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        logger.info("✓ OpenAI API connection successful")
    except Exception as e:
        logger.error(f"✗ OpenAI API connection failed: {e}")


async def main():
    """Run all tests."""
    logger.info("=== Fort Worth Research Agent Diagnostic ===\n")
    
    # Check API keys first
    await check_api_keys()
    
    # Test components
    await test_basic_agent()
    await test_research_workflow()
    await test_data_sync()
    await test_full_pipeline()
    
    logger.info("\n=== Diagnostic Complete ===")


if __name__ == "__main__":
    asyncio.run(main())