# Structured Output Guide for TOP Compliance

## Overview

This guide explains how to use structured outputs with the Fort Worth Wiki Engine to ensure full Texas Ontology Protocol (TOP) compliance. Structured outputs leverage Pydantic models to provide type-safe, validated data extraction from AI agents.

## Key Components

### 1. Structured Models (`src/models/top/structured.py`)

#### Core Models

- **`TOPEpisodeData`**: Primary container for episode data
  ```python
  episode = TOPEpisodeData(
      entities=[...],        # List of StructuredEntity
      relationships=[...],   # List of StructuredRelationship
      metadata={...}        # Optional metadata
  )
  ```

- **`StructuredEntity`**: Validated TOP entity
  ```python
  entity = StructuredEntity(
      entity_type=TOPEntityType.MAYOR,
      top_id="fwtx:mayor:current",
      properties={"entity_name": "Mayor Mattie Parker", ...},
      source="https://fortworthtexas.gov",
      confidence=ConfidenceLevel.HIGH
  )
  ```

- **`StructuredRelationship`**: Validated TOP relationship
  ```python
  rel = StructuredRelationship(
      relationship_type=TOPRelationshipType.SERVES,
      source_entity="fwtx:councilmember:district-1",
      target_entity="fwtx:district:1",
      properties={...}
  )
  ```

#### Helper Models

- **`MayorData`**: Specialized model for mayor information
- **`DepartmentData`**: Department-specific fields
- **`CouncilMemberData`**: Council member details

### 2. AI Agent Integration

#### Using Structured Output with Agents

```python
from agno.agent import Agent
from src.models.top.structured import TOPEpisodeData

agent = Agent(
    name="Research Agent",
    model=OpenAIChat(id="gpt-4o"),
    response_model=TOPEpisodeData,  # Structured output!
    use_json_mode=True
)

response = agent.run("Research Fort Worth departments")
episode_data: TOPEpisodeData = response.content  # Type-safe!
```

#### Benefits

1. **Type Safety**: No more JSON parsing errors
2. **Validation**: Automatic field validation
3. **Consistency**: All agents produce same format
4. **Documentation**: Self-documenting models

### 3. Data Flow

```
Raw Data → Structured Models → Validation → Episodes → Graphiti
```

1. **Input**: AI agents or file parsers produce data
2. **Structure**: Data is validated against Pydantic models
3. **Validation**: Entity references and TOP IDs are checked
4. **Output**: Clean episodes ready for knowledge graph

## Usage Examples

### Example 1: Research with Structured Output

```python
# Research mayor with type-safe output
mayor_agent = Agent(
    name="Mayor Researcher",
    model=OpenAIChat(id="gpt-4o"),
    response_model=MayorData,
    use_json_mode=True
)

response = mayor_agent.run("Research Fort Worth mayor")
mayor: MayorData = response.content

# Convert to TOP entity
entity = mayor.to_top_entity()
```

### Example 2: Batch Entity Creation

```python
# Create complete episode
episode = TOPEpisodeData()

# Add entities
for dept_data in department_list:
    entity = StructuredEntity(
        entity_type="Department",
        top_id=f"fwtx:dept:{dept_data['id']}",
        properties={...}
    )
    episode.entities.append(entity)

# Add relationships
for entity in episode.entities:
    rel = StructuredRelationship(
        relationship_type="PartOf",
        source_entity=entity.top_id,
        target_entity="fwtx:city:fort-worth"
    )
    episode.relationships.append(rel)

# Validate
missing = episode.validate_entity_references()
```

### Example 3: Data Loader Integration

```python
from src.models.top.structured import TOPEpisodeData

class DataLoader:
    def create_structured_entities(self, raw_data):
        episode_data = TOPEpisodeData()
        
        # Create entities with validation
        city = StructuredEntity(
            entity_type="HomeRuleCity",
            top_id="fwtx:city:fort-worth",
            properties={...}
        )
        episode_data.entities.append(city)
        
        # Return validated data
        return episode_data.model_dump()
```

## Validation Rules

### TOP ID Format

- Must start with `fwtx:`
- Format: `fwtx:type:identifier`
- Examples:
  - `fwtx:mayor:current`
  - `fwtx:dept:police`
  - `fwtx:district:1`

### Required Fields

All entities must have:
- `entity_type`: Valid TOP entity type
- `top_id`: Unique identifier
- `properties.entity_name`: Human-readable name
- `source`: Data source
- `confidence`: Data confidence level

### Temporal Data

- Use ISO format: `"2024-01-01"`
- `valid_from` required for temporal entities
- `valid_until` optional (null = currently valid)

## Best Practices

1. **Always Validate**
   ```python
   missing = episode_data.validate_entity_references()
   if missing:
       logger.warning(f"Missing entities: {missing}")
   ```

2. **Use Enums**
   ```python
   from src.models.top.structured import TOPEntityType
   
   entity_type = TOPEntityType.MAYOR  # Type-safe!
   ```

3. **Handle Errors**
   ```python
   try:
       entity = StructuredEntity(**data)
   except ValidationError as e:
       logger.error(f"Invalid entity data: {e}")
   ```

4. **Document Sources**
   ```python
   entity = StructuredEntity(
       source="https://fortworthtexas.gov/mayor",
       confidence=ConfidenceLevel.HIGH
   )
   ```

## Common Patterns

### Pattern 1: Entity with Relationships

```python
# Create entity and its relationships together
def create_council_member(name: str, district: int):
    member = StructuredEntity(
        entity_type="CouncilMember",
        top_id=f"fwtx:councilmember:district-{district}",
        properties={"entity_name": f"Council Member {name}", ...}
    )
    
    serves = StructuredRelationship(
        relationship_type="Serves",
        source_entity=member.top_id,
        target_entity=f"fwtx:district:{district}"
    )
    
    return member, serves
```

### Pattern 2: Bulk Processing

```python
def process_departments(dept_list: List[Dict]):
    episode = TOPEpisodeData()
    
    for dept in dept_list:
        entity = DepartmentData(**dept).to_top_entity(
            top_id=f"fwtx:dept:{dept['id']}"
        )
        episode.entities.append(entity)
    
    return episode
```

### Pattern 3: Research Pipeline

```python
async def research_pipeline(topic: str):
    # 1. Research with AI
    agent = Agent(response_model=TOPEpisodeData)
    response = agent.run(f"Research {topic}")
    
    # 2. Validate results
    episode_data = response.content
    missing = episode_data.validate_entity_references()
    
    # 3. Store in knowledge graph
    await graphiti.add_episode_bulk([
        RawEpisode(
            name=topic,
            content=episode_data.to_episode_content(),
            source=EpisodeType.json
        )
    ])
```

## Troubleshooting

### Common Issues

1. **Validation Errors**
   - Check required fields
   - Verify TOP ID format
   - Ensure entity_name in properties

2. **Missing Entity References**
   - All relationships must reference existing entities
   - Create entities before relationships
   - Use `validate_entity_references()`

3. **Type Mismatches**
   - Use proper enums for types
   - Check field types match model
   - Review Pydantic error messages

### Debug Tips

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Print model schema
print(TOPEpisodeData.model_json_schema())

# Validate data manually
try:
    TOPEpisodeData.model_validate(data)
except ValidationError as e:
    print(e.json(indent=2))
```

## Next Steps

1. Review `examples/structured_research.py` for complete examples
2. Check `src/models/top/structured.py` for all available models
3. See `docs/TOP_COMPLIANCE_ASSESSMENT.md` for compliance details

Remember: Structured outputs ensure data quality and TOP compliance!