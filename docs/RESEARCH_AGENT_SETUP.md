# AI Research Agent Setup Guide

## Overview

The Fort Worth Wiki includes AI research agents that can automatically gather and structure municipal data from live sources. However, by default, these agents are not activated to prevent unnecessary API calls during development.

## Quick Start

To enable AI research agents and populate your knowledge graph with Fort Worth data:

### Option 1: Enable During Startup (Recommended)

1. Edit your `.env` file:
   ```
   LOAD_INITIAL_DATA=true
   SYNC_MODE=live
   ```

2. Restart the application:
   ```bash
   uv run wiki.py
   ```

The research agents will automatically run during initialization and populate the knowledge graph.

### Option 2: Run Research Manually

If you want to run research without changing your `.env`:

```bash
uv run scripts/run_research.py
```

This will:
- Load TOP-compliant base data
- Run AI research agents for 6 topics:
  - City Information
  - Current Mayor
  - City Council Members
  - City Departments
  - City Services
  - Governance Structure

### Option 3: Test Research Agent

To test if the research agent is working properly:

```bash
uv run scripts/test_research_agent.py
```

This diagnostic script will:
- Check API key configuration
- Test basic agent functionality
- Run a sample research task
- Show detailed logs

## Configuration

### Environment Variables

- `LOAD_INITIAL_DATA`: Set to `true` to load data on startup
- `SYNC_MODE`: Choose data loading mode
  - `initial`: Load from local files only (faster, no API calls)
  - `live`: Use AI agents to research current data (requires OpenAI API)
- `OPENAI_API_KEY`: Required for AI research agents
- `AGENT_CACHE_ENABLED`: Enable caching of research results (default: true)
- `AGENT_CACHE_TTL_HOURS`: Cache duration in hours (default: 24)

### What the Research Agent Does

When enabled, the AI research agent:

1. **Creates Research Tasks**: Generates queries for Fort Worth municipal data
2. **Uses AI Team**: Coordinates multiple AI agents:
   - Web Research Agent: Searches for official information
   - Data Structure Agent: Converts findings to TOP format
   - County Integration Analyst: Analyzes regional relationships
3. **Produces Structured Data**: All output follows Texas Ontology Protocol
4. **Populates Knowledge Graph**: Creates entities and relationships

## Troubleshooting

### Research Agent Not Running

If you see logs like:
```
Graphiti initialization started (basic setup only - set LOAD_INITIAL_DATA=true to load data)
```

This means `LOAD_INITIAL_DATA` is set to `false`. Either:
1. Update your `.env` file and restart
2. Run `uv run scripts/run_research.py` manually

### No Research Output

Check the logs for:
- "Starting research for all tasks..."
- "Research completed - adding X episodes to graph"

If these are missing, the research workflow may have failed. Run the diagnostic:
```bash
uv run scripts/test_research_agent.py
```

### API Key Issues

Ensure your OpenAI API key is set:
```bash
echo $OPENAI_API_KEY
```

The research agent requires a valid OpenAI API key to function.

## Expected Results

After successful research, you should have:
- Fort Worth city entity with current population
- Mayor Mattie Parker with term information
- All 9 city council members and districts
- Major city departments with budgets
- City services and contact information
- Governance structure relationships

Test with:
```bash
curl http://localhost:8001/chat -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "Who is the mayor of Fort Worth?"}'
```