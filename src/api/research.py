"""
API endpoints for AI research operations.
"""

from fastapi import APIRouter, Depends, HTTPException

from src.middleware.auth import get_api_key
from src.services.agent.researcher import FortWorthResearchWorkflow
from src.services.graphiti.index import graphiti
from src.models.research import ResearchRequest, ResearchResponse

router = APIRouter(prefix="/api/research", tags=["research"])

@router.post("/topic", response_model=ResearchResponse)
async def research_topic(
    request: ResearchRequest,
    authenticated: bool = Depends(get_api_key)
):
    """
    Research a specific Fort Worth topic using AI agents.
    
    - **topic**: Topic to research (e.g., "current mayor", "city budget", "council districts")
    - **data_requirements**: Specific data points to extract
    - **search_queries**: Optional specific search queries to use
    """
    try:
        # Create research task
        research_task = {
            "name": request.topic,
            "config": {
                "search_queries": request.search_queries or [
                    f"Fort Worth Texas {request.topic} 2024",
                    f"Fort Worth {request.topic} official information"
                ],
                "data_needed": request.data_requirements or []
            }
        }
        
        # Run research
        workflow = FortWorthResearchWorkflow(graphiti)
        episodes = await workflow.research_all_tasks([research_task])
        
        # Add episodes to graph
        if episodes:
            await graphiti.add_episode_bulk(episodes)
        
        return ResearchResponse(
            topic=request.topic,
            status="success",
            episodes_created=len(episodes),
            results_summary=f"Researched {request.topic} and created {len(episodes)} knowledge graph entries"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")


@router.get("/tasks")
async def get_available_research_tasks(authenticated: bool = Depends(get_api_key)):
    """
    Get list of available research tasks that can be performed.
    """
    return {
        "available_tasks": [
            {
                "topic": "current_mayor",
                "description": "Research current Fort Worth mayor information",
                "data_points": ["name", "term_dates", "contact_info", "initiatives"]
            },
            {
                "topic": "city_council",
                "description": "Research city council members and districts",
                "data_points": ["member_names", "districts", "committees", "meeting_schedule"]
            },
            {
                "topic": "city_budget",
                "description": "Research current fiscal year budget",
                "data_points": ["total_budget", "department_allocations", "tax_rate", "major_projects"]
            },
            {
                "topic": "city_services",
                "description": "Research city services and departments",
                "data_points": ["service_names", "departments", "contact_info", "online_portals"]
            },
            {
                "topic": "recent_ordinances",
                "description": "Research recently passed ordinances",
                "data_points": ["ordinance_numbers", "titles", "effective_dates", "summaries"]
            }
        ]
    }


@router.post("/custom")
async def custom_research(
    prompt: str,
    authenticated: bool = Depends(get_api_key)
):
    """
    Perform custom research with a specific prompt.
    
    This endpoint allows direct specification of what to research about Fort Worth.
    """
    try:
        # Create custom research task
        research_task = {
            "name": "Custom Research",
            "config": {
                "search_queries": [prompt],
                "data_needed": ["all_relevant_information"]
            }
        }
        
        workflow = FortWorthResearchWorkflow(graphiti)
        
        # Run the research directly and get the response
        response_content = []
        for response in workflow.run(research_task):
            if response.content:
                response_content.append(response.content)
        
        # Get episodes from session state
        episodes = workflow.session_state.get("Custom Research_episodes", [])
        
        # Add to graph if we have episodes
        if episodes:
            await graphiti.add_episode_bulk(episodes)
        
        return {
            "status": "success",
            "prompt": prompt,
            "episodes_created": len(episodes),
            "research_output": "\n".join(response_content) if response_content else "Research completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Custom research failed: {str(e)}")