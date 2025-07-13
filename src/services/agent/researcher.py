"""
Fort Worth Municipal Research Agent using Agno.

This module implements an AI agent team for researching and structuring
Fort Worth municipal government data from various sources.
"""

from typing import Iterator, Dict, Any, List
from datetime import datetime
import json
import logging

from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from agno.utils.pprint import pprint_run_response
from agno.workflow import Workflow

from graphiti_core.nodes import EpisodeType
from graphiti_core.utils.bulk_utils import RawEpisode

# Import structured output models
from src.models.top.structured import (
    TOPEpisodeData,
    StructuredEntity,
    StructuredRelationship,
    ResearchOutput,
    MayorData,
    DepartmentData,
    CouncilMemberData
)

logger = logging.getLogger(__name__)


# Import settings to get model configurations
from src.config import settings

# Log OpenAI configuration
logger.info(f"Using OpenAI model: {settings.OPENAI_MODEL}")
if settings.OPENAI_API_KEY:
    logger.info("OpenAI API authentication configured")
else:
    logger.warning("No OPENAI_API_KEY found - OpenAI models will not work")

# Helper function to create OpenAI model
def create_openai_model(model_id: str, **kwargs):
    """Create an OpenAI model."""
    return OpenAIChat(
        id=model_id,
        **kwargs
    )

# Define specialized agents for different research tasks
# Web researcher uses OpenAI for accurate, up-to-date information
web_researcher = Agent(
    name="Web Research Agent",
    role="Research Fort Worth government websites and official sources",
    model=create_openai_model(settings.OPENAI_MODEL),
    tools=[DuckDuckGoTools()],
    instructions=[
        "Focus on official Fort Worth government websites (.gov domains)",
        "Always include source URLs and dates",
        "Verify information from multiple sources when possible",
        "Extract structured data according to Texas Ontology Protocol (TOP)",
        "Ensure factual accuracy of government data",
    ],
    add_datetime_to_instructions=True,
    show_tool_calls=True,
    # Enable structured output when researching specific entity types
    response_model=None  # Will be set dynamically based on task
)

data_structurer = Agent(
    name="Data Structure Agent", 
    role="Structure raw data into Texas Ontology Protocol compliant format",
    model=create_openai_model(settings.OPENAI_MODEL),
    instructions=[
        "Convert unstructured data into TOP-compliant JSON format",
        "Use appropriate entity types: HomeRuleCity, Mayor, Department, etc.",
        "Include temporal data (valid_from, valid_until) for all entities",
        "Add source attribution with confidence levels",
        "Ensure all required fields are populated",
        "Follow the exact structure of TOPEpisodeData model",
    ],
    add_datetime_to_instructions=True,
    # Use structured output for data structuring
    response_model=TOPEpisodeData,
    use_json_mode=True
)

county_analyst = Agent(
    name="County Integration Analyst",
    role="Analyze Fort Worth's relationship with Tarrant County and Texas state structure",
    model=create_openai_model(settings.OPENAI_MODEL),
    tools=[DuckDuckGoTools()],
    instructions=[
        "Research Fort Worth's position within Tarrant County",
        "Identify overlapping jurisdictions and shared services",
        "Analyze intergovernmental agreements",
        "Map relationships between city, county, and state entities",
        "Verify jurisdictional boundaries and legal structures",
    ],
    add_datetime_to_instructions=True,
    show_tool_calls=True,
)

# Create the research team with OpenAI model
fort_worth_research_team = Team(
    name="Fort Worth Municipal Research Team",
    mode="coordinate",
    model=create_openai_model(settings.OPENAI_MODEL),
    members=[web_researcher, data_structurer, county_analyst],
    tools=[ReasoningTools(add_instructions=True)],
    instructions=[
        "Collaborate to research comprehensive Fort Worth municipal data",
        "Ensure all data follows Texas Ontology Protocol (TOP) standards",
        "Cross-verify information between team members",
        "Output structured JSON data ready for knowledge graph ingestion",
        "Include confidence levels and source citations for all data points",
        "Prioritize official government sources",
    ],
    markdown=True,
    show_members_responses=True,
    enable_agentic_context=True,
    add_datetime_to_instructions=True,
    success_criteria="The team has provided complete, structured Fort Worth municipal data with proper TOP formatting, source citations, and confidence levels.",
)


class FortWorthResearchWorkflow(Workflow):
    """Workflow for researching Fort Worth municipal data."""
    
    team = fort_worth_research_team
    
    def __init__(self, graphiti=None):
        super().__init__()
        self.graphiti = graphiti
        self.research_cache = {}
        self.cache_enabled = settings.AGENT_CACHE_ENABLED
        self.cache_ttl_hours = settings.AGENT_CACHE_TTL_HOURS
    
    def run(self, research_task: Dict[str, Any]) -> Iterator[RunResponse]:
        """
        Run research workflow for a specific task.
        
        Args:
            research_task: Dictionary containing research configuration
            
        Yields:
            RunResponse objects with research results
        """
        task_name = research_task.get('name', 'Unknown Task')
        
        # Check cache if enabled
        if self.cache_enabled and task_name in self.research_cache:
            cache_entry = self.research_cache[task_name]
            cache_age_hours = (datetime.now() - cache_entry['timestamp']).total_seconds() / 3600
            
            if cache_age_hours < self.cache_ttl_hours:
                logger.info(f"Using cached results for '{task_name}' (age: {cache_age_hours:.1f} hours)")
                yield RunResponse(
                    run_id=self.run_id,
                    content=cache_entry['content']
                )
                return
            else:
                logger.info(f"Cache expired for '{task_name}' (age: {cache_age_hours:.1f} hours)")
        
        # Build research prompt
        prompt = self._build_research_prompt(research_task)
        
        logger.info(f"Starting research for '{task_name}'")
        
        # Run the team research
        logger.info(f"Running team research with prompt (first 200 chars): {prompt[:200]}...")
        
        try:
            yield from self.team.run(prompt, stream=True)
        except Exception as e:
            logger.error(f"Team research failed: {e}", exc_info=True)
            raise
        
        # Cache the results if enabled
        if self.cache_enabled and self.team.run_response:
            logger.info(f"Caching results for '{task_name}'")
            self.research_cache[task_name] = {
                'content': self.team.run_response.content,
                'timestamp': datetime.now()
            }
            
            # Process and structure the results
            logger.info("Processing research results...")
            episodes = self._process_research_results(
                self.team.run_response.content,
                task_name
            )
            logger.info(f"Created {len(episodes)} episodes from research")
            
            # Store in session state for later use
            self.session_state[f"{task_name}_episodes"] = episodes
        else:
            logger.warning(f"No response to cache for '{task_name}'")
    
    def _build_research_prompt(self, research_task: Dict[str, Any]) -> str:
        """Build detailed research prompt from task configuration."""
        config = research_task.get('config', {})
        name = research_task.get('name', 'Unknown')
        
        prompt = f"""Research Task: {name}

Please research the following information about Fort Worth, Texas municipal government:

"""
        
        # Add search queries
        if 'search_queries' in config:
            prompt += "Use these search queries:\n"
            queries = config['search_queries']
            if isinstance(queries, list):
                for query in queries:
                    prompt += f"- {query}\n"
            else:
                prompt += f"- {queries}\n"
            prompt += "\n"
        
        # Add data requirements
        if 'data_needed' in config:
            prompt += "Extract these specific data points:\n"
            for data_point in config['data_needed']:
                prompt += f"- {data_point}\n"
            prompt += "\n"
        
        # Add URLs to check
        if 'fetch_url' in config:
            prompt += f"Primary source to check: {config['fetch_url']}\n\n"
        
        # Add structured output format requirements
        prompt += """Output Requirements:
1. Structure all findings as JSON following Texas Ontology Protocol (TOP)
2. Use appropriate entity types:
   - Government: HomeRuleCity, Department, Division, Committee
   - Political: Mayor, CouncilMember, CityManager, AppointedPosition, ElectedPosition
   - Legal: Charter, Ordinance, Resolution, Policy
   - Geographic: CouncilDistrict, Precinct, VotingLocation
   - Person: for individuals holding positions
3. Include temporal data (valid_from, valid_until) where applicable
4. Add source URLs and confidence levels for each data point
5. Use proper TOP IDs format: "fwtx:type:identifier" (e.g., "fwtx:mayor:current", "fwtx:dept:police")
6. Separate entities and relationships

IMPORTANT: Return your results in the following JSON structure:
{
    "entities": [
        {
            "entity_type": "Mayor",
            "top_id": "fwtx:mayor:current",
            "properties": {
                "entity_name": "Mayor Mattie Parker",
                "person_name": "Mattie Parker",
                "term_start": "2021-06-01",
                "term_end": "2025-05-31",
                "election_type": "at-large",
                "political_party": "Republican"
            },
            "source": "https://fortworthtexas.gov/mayor",
            "confidence": "high",
            "valid_from": "2021-06-01"
        },
        {
            "entity_type": "Department",
            "top_id": "fwtx:dept:police",
            "properties": {
                "entity_name": "Fort Worth Police Department",
                "department_type": "public_safety",
                "chief": "Neil Noakes",
                "budget_fy2024": 328000000,
                "employee_count": 1700,
                "parent_organization": "fwtx:city:fort-worth"
            },
            "source": "https://fortworthpd.com",
            "confidence": "high",
            "valid_from": "1873-01-01"
        }
    ],
    "relationships": [
        {
            "relationship_type": "Governs",
            "source_entity": "fwtx:mayor:current",
            "target_entity": "fwtx:city:fort-worth",
            "properties": {
                "start_date": "2021-06-01",
                "election_date": "2021-05-01"
            },
            "source": "https://fortworthtexas.gov/mayor",
            "confidence": "high"
        },
        {
            "relationship_type": "PartOf",
            "source_entity": "fwtx:dept:police",
            "target_entity": "fwtx:city:fort-worth",
            "properties": {
                "relationship_type": "administrative"
            },
            "source": "https://fortworthpd.com",
            "confidence": "high"
        }
    ]
}

Valid relationship types: Governs, HasJurisdictionOver, HoldsPosition, AppointedBy, ElectedTo, SupersededBy, PartOf, ReportsTo, Serves

Ensure all data is properly structured and validated according to TOP specifications.
"""
        
        return prompt
    
    def _process_research_results(self, content: str, task_name: str) -> List[RawEpisode]:
        """Process research results into Graphiti episodes."""
        episodes = []
        
        try:
            # Try to extract JSON from the content
            # The AI response might have JSON embedded in markdown
            import re
            json_pattern = r'```json\s*([\s\S]*?)\s*```'
            json_matches = re.findall(json_pattern, content)
            
            if json_matches:
                for json_str in json_matches:
                    try:
                        data = json.loads(json_str)
                        
                        # Try to parse as TOPEpisodeData
                        if 'entities' in data and 'relationships' in data:
                            episode_data = TOPEpisodeData(**data)
                            
                            # Validate entity references
                            missing_ids = episode_data.validate_entity_references()
                            if missing_ids:
                                logger.warning(f"Missing entity references: {missing_ids}")
                            
                            # Create episode from structured data
                            episodes.append(RawEpisode(
                                name=f"{task_name} - Structured Data",
                                content=episode_data.to_episode_content(),
                                source=EpisodeType.json,
                                source_description=f"AI researched - {task_name}",
                                reference_time=datetime.now()
                            ))
                        elif isinstance(data, list):
                            # Legacy format support
                            for item in data:
                                episode = self._create_episode_from_data(item, task_name)
                                if episode:
                                    episodes.append(episode)
                        else:
                            episode = self._create_episode_from_data(data, task_name)
                            if episode:
                                episodes.append(episode)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse JSON from research results")
                    except Exception as e:
                        logger.warning(f"Failed to parse structured data: {e}")
            
            # If no JSON found, create a text episode with the full content
            if not episodes:
                episodes.append(RawEpisode(
                    name=f"Research Results - {task_name}",
                    content=content,
                    source=EpisodeType.text,
                    source_description=f"AI research results for {task_name}",
                    reference_time=datetime.now()
                ))
                
        except Exception as e:
            logger.error(f"Error processing research results: {e}")
            
        return episodes
    
    def _create_episode_from_data(self, data: Dict[str, Any], task_name: str) -> RawEpisode:
        """Create a Graphiti episode from structured data."""
        if 'entity_type' in data:
            # Try to create a StructuredEntity for validation
            try:
                entity = StructuredEntity(**data)
                entity_name = entity.properties.get('entity_name', 'Unknown')
                episode_name = f"{entity.entity_type} - {entity_name}"
                return RawEpisode(
                    name=episode_name,
                    content=entity.model_dump_json(indent=2),
                    source=EpisodeType.json,
                    source_description=f"AI researched - {task_name}",
                    reference_time=datetime.now()
                )
            except Exception as e:
                logger.warning(f"Entity validation failed: {e}")
                # Fall back to raw data
                entity_name = data.get('properties', {}).get('entity_name', 'Unknown')
                episode_name = f"{data['entity_type']} - {entity_name}"
                return RawEpisode(
                    name=episode_name,
                    content=json.dumps(data),
                    source=EpisodeType.json,
                    source_description=f"AI researched - {task_name}",
                    reference_time=datetime.now()
                )
        elif 'relationship_type' in data:
            # Try to create a StructuredRelationship for validation
            try:
                rel = StructuredRelationship(**data)
                episode_name = f"Relationship - {rel.relationship_type}"
                return RawEpisode(
                    name=episode_name,
                    content=rel.model_dump_json(indent=2),
                    source=EpisodeType.json,
                    source_description=f"AI researched relationship - {task_name}",
                    reference_time=datetime.now()
                )
            except Exception as e:
                logger.warning(f"Relationship validation failed: {e}")
                # Fall back to raw data
                episode_name = f"Relationship - {data['relationship_type']}"
                return RawEpisode(
                    name=episode_name,
                    content=json.dumps(data),
                    source=EpisodeType.json,
                    source_description=f"AI researched relationship - {task_name}",
                    reference_time=datetime.now()
                )
        return None
    
    async def research_all_tasks(self, tasks: List[Dict[str, Any]]) -> List[RawEpisode]:
        """Research all tasks and return episodes."""
        all_episodes = []
        
        for task in tasks:
            logger.info(f"Researching: {task['name']}")
            
            # Run the research
            response_iter = self.run(task)
            
            # Consume the iterator to get results
            for response in response_iter:
                if response.content:
                    logger.debug(f"Research response: {response.content[:200]}...")
            
            # Get episodes from session state
            task_episodes = self.session_state.get(f"{task['name']}_episodes", [])
            all_episodes.extend(task_episodes)
        
        return all_episodes


# Standalone function for direct agent research
async def research_fort_worth_topic(topic: str, data_requirements: List[str] = None) -> Dict[str, Any]:
    """
    Research a specific Fort Worth topic using the agent team.
    
    Args:
        topic: Topic to research
        data_requirements: Specific data points to extract
        
    Returns:
        Dictionary with research results
    """
    workflow = FortWorthResearchWorkflow()
    
    research_task = {
        "name": topic,
        "config": {
            "search_queries": [f"Fort Worth Texas {topic} 2024"],
            "data_needed": data_requirements or []
        }
    }
    
    results = []
    for response in workflow.run(research_task):
        if response.content:
            results.append(response.content)
    
    return {
        "topic": topic,
        "results": results,
        "episodes": workflow.session_state.get(f"{topic}_episodes", [])
    }


if __name__ == "__main__":
    # Example usage
    workflow = FortWorthResearchWorkflow()
    
    test_task = {
        "name": "Current Mayor Information",
        "config": {
            "search_queries": [
                "Fort Worth Texas mayor Mattie Parker 2024",
                "Fort Worth mayor contact information office"
            ],
            "data_needed": [
                "mayor_name",
                "term_dates", 
                "contact_info",
                "major_initiatives"
            ]
        }
    }
    
    response = workflow.run(test_task)
    pprint_run_response(response, markdown=True, show_time=True)