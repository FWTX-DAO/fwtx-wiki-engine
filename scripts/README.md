# Fort Worth Wiki Scripts

This directory contains utility scripts for development, testing, and maintenance of the Fort Worth Wiki system.

## Scripts

### `init_top_data.py`
Initializes the Fort Worth Wiki knowledge graph with TOP (Texas Ontology Protocol) compliant data.

```bash
uv run scripts/init_top_data.py
```

**Purpose**: Loads structured Fort Worth municipal data into the graph database and verifies TOP compliance.

### `reset_and_init.py`
Database maintenance script that resets FalkorDB and reinitializes it with TOP structure.

```bash
uv run scripts/reset_and_init.py
```

**Purpose**: Clears all data from FalkorDB and recreates the knowledge graph structure. Useful for development and testing.

### `run_research.py`
Manually triggers the AI research agent to populate Fort Worth data using live web research.

```bash
uv run scripts/run_research.py
```

**Purpose**: Overrides environment settings to force research mode and populate the knowledge graph with current Fort Worth municipal data.

### `test_research_agent.py`
Diagnostic tool for testing and debugging the AI research agent functionality.

```bash
uv run scripts/test_research_agent.py
```

**Purpose**: Tests basic agent operations, research workflow, data sync, and API connections. Useful for troubleshooting research issues.

## Usage Notes

- All scripts should be run from the project root directory
- Ensure your `.env` file is properly configured with required API keys
- Scripts may take several minutes to complete depending on network conditions and AI agent responses
- Check the logs for detailed progress and error information