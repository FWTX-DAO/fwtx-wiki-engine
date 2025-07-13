#!/usr/bin/env python3
"""
Example of using structured outputs with the Fort Worth research agent.

This demonstrates how to leverage Pydantic models for type-safe,
TOP-compliant data extraction from AI research.
"""

import asyncio
from datetime import datetime

from agno.agent import Agent
from agno.models.openai import OpenAIChat

from src.models.top.structured import (
    TOPEpisodeData,
    MayorData,
    DepartmentData,
    CouncilMemberData,
    StructuredEntity,
    StructuredRelationship
)
from src.config import settings


async def research_mayor_structured():
    """Research Fort Worth mayor using structured output."""
    
    # Create agent with structured output for mayor data
    mayor_researcher = Agent(
        name="Mayor Research Agent",
        role="Research Fort Worth mayor information",
        model=OpenAIChat(id=settings.OPENAI_MODEL),
        instructions=[
            "Research the current Fort Worth mayor",
            "Find official information from fortworthtexas.gov",
            "Extract all available data fields"
        ],
        response_model=MayorData,  # Use structured output!
        use_json_mode=True
    )
    
    # Run research
    response = mayor_researcher.run(
        "Research the current Fort Worth mayor Mattie Parker. "
        "Find her term dates, contact information, and political affiliation."
    )
    
    if response.content:
        # response.content is now a MayorData object!
        mayor_data: MayorData = response.content
        print(f"Mayor: {mayor_data.person_name}")
        print(f"Term: {mayor_data.term_start} to {mayor_data.term_end}")
        
        # Convert to TOP entity
        top_entity = mayor_data.to_top_entity()
        print(f"\nTOP Entity: {top_entity.model_dump_json(indent=2)}")
        
        return top_entity


async def research_departments_batch():
    """Research multiple departments using structured output."""
    
    # Create agent that returns complete episode data
    dept_researcher = Agent(
        name="Department Research Agent",
        role="Research Fort Worth city departments",
        model=OpenAIChat(id=settings.OPENAI_MODEL),
        instructions=[
            "Research Fort Worth city departments",
            "Create proper TOP entities and relationships",
            "Include budget and employee data where available"
        ],
        response_model=TOPEpisodeData,  # Full episode structure
        use_json_mode=True
    )
    
    response = dept_researcher.run(
        "Research Fort Worth Police and Fire departments. "
        "Include their budgets, employee counts, and leadership. "
        "Create PartOf relationships to the city."
    )
    
    if response.content:
        episode_data: TOPEpisodeData = response.content
        
        print(f"Found {len(episode_data.entities)} entities")
        print(f"Found {len(episode_data.relationships)} relationships")
        
        # Validate entity references
        missing = episode_data.validate_entity_references()
        if missing:
            print(f"Warning: Missing entities: {missing}")
        
        # Access specific entities
        for entity in episode_data.entities:
            if entity.entity_type == "Department":
                print(f"\nDepartment: {entity.properties['entity_name']}")
                print(f"  Budget: ${entity.properties.get('budget_amount', 'N/A'):,}")
                print(f"  Employees: {entity.properties.get('employee_count', 'N/A')}")
        
        return episode_data


async def research_council_structured():
    """Research city council with automatic entity/relationship creation."""
    
    # Create specialized agent for council research
    council_researcher = Agent(
        name="Council Research Agent",
        role="Research Fort Worth city council members",
        model=OpenAIChat(id=settings.OPENAI_MODEL),
        instructions=[
            "Research all Fort Worth city council members",
            "Include district numbers and term information",
            "Create CouncilMember and CouncilDistrict entities",
            "Create Serves relationships between members and districts"
        ],
        response_model=TOPEpisodeData,
        use_json_mode=True
    )
    
    response = council_researcher.run(
        "Research Fort Worth city council members for all 9 districts. "
        "Include their names, districts, and current terms."
    )
    
    if response.content:
        episode_data: TOPEpisodeData = response.content
        
        # Group by type
        council_members = [e for e in episode_data.entities if e.entity_type == "CouncilMember"]
        districts = [e for e in episode_data.entities if e.entity_type == "CouncilDistrict"]
        serves_rels = [r for r in episode_data.relationships if r.relationship_type == "Serves"]
        
        print(f"Council Members: {len(council_members)}")
        print(f"Districts: {len(districts)}")
        print(f"Serves Relationships: {len(serves_rels)}")
        
        # Display council structure
        for district in sorted(districts, key=lambda d: d.properties.get('district_number', 0)):
            dist_num = district.properties.get('district_number')
            print(f"\nDistrict {dist_num}:")
            
            # Find council member for this district
            for rel in serves_rels:
                if rel.target_entity == district.top_id:
                    member = episode_data.get_entity_by_id(rel.source_entity)
                    if member:
                        print(f"  Representative: {member.properties.get('person_name')}")
                        print(f"  Term ends: {member.properties.get('term_end')}")
        
        return episode_data


async def create_complete_city_episode():
    """Create a complete city episode with all entity types."""
    
    # This demonstrates manual creation of structured data
    episode = TOPEpisodeData()
    
    # Add city entity
    city = StructuredEntity(
        entity_type="HomeRuleCity",
        top_id="fwtx:city:fort-worth",
        properties={
            "entity_name": "City of Fort Worth",
            "population": 956709,
            "incorporation_date": "1873-03-19",
            "charter_adopted": "1924-01-01",
            "governmental_form": "council-manager"
        },
        source="Manual entry",
        confidence="high",
        valid_from="1873-03-19"
    )
    episode.entities.append(city)
    
    # Add mayor using helper
    mayor_data = MayorData(
        person_name="Mattie Parker",
        term_start="2021-06-01",
        term_end="2025-05-31",
        political_party="Republican",
        contact_email="mayor@fortworthtexas.gov"
    )
    episode.entities.append(mayor_data.to_top_entity())
    
    # Add relationship
    governs = StructuredRelationship(
        relationship_type="Governs",
        source_entity="fwtx:mayor:current",
        target_entity="fwtx:city:fort-worth",
        properties={"elected": "2021-05-01"},
        source="Manual entry",
        confidence="high"
    )
    episode.relationships.append(governs)
    
    # Validate
    missing = episode.validate_entity_references()
    if missing:
        print(f"Validation failed - missing entities: {missing}")
    else:
        print("Episode validation passed!")
        print(f"\nEpisode JSON:\n{episode.to_episode_content()}")
    
    return episode


async def main():
    """Run all examples."""
    print("=== Fort Worth Structured Research Examples ===\n")
    
    # Example 1: Research mayor with structured output
    print("1. Researching Mayor with Structured Output...")
    try:
        mayor = await research_mayor_structured()
        print("✓ Mayor research complete\n")
    except Exception as e:
        print(f"✗ Mayor research failed: {e}\n")
    
    # Example 2: Research departments in batch
    print("2. Researching Departments with Episode Structure...")
    try:
        depts = await research_departments_batch()
        print("✓ Department research complete\n")
    except Exception as e:
        print(f"✗ Department research failed: {e}\n")
    
    # Example 3: Research council with relationships
    print("3. Researching City Council with Relationships...")
    try:
        council = await research_council_structured()
        print("✓ Council research complete\n")
    except Exception as e:
        print(f"✗ Council research failed: {e}\n")
    
    # Example 4: Manual structured data creation
    print("4. Creating Manual Structured Episode...")
    try:
        manual = await create_complete_city_episode()
        print("✓ Manual episode creation complete\n")
    except Exception as e:
        print(f"✗ Manual episode creation failed: {e}\n")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())