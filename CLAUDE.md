# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fort Worth Wiki is a knowledge graph-based system for Fort Worth municipal information using FastAPI, FalkorDB, and Graphiti-core with Google GenAI integration for GraphRAG (Graph Retrieval-Augmented Generation).

## Development Commands

### Setup and Running
```bash
# Install dependencies (requires Python 3.13+)
uv sync

# Start FalkorDB (required for knowledge graph)
docker run -p 6379:6379 -p 3000:3000 -it --rm falkordb/falkordb:latest

# Run the application
uv run wiki.py
```

### Environment Configuration
Copy `.env.example` to `.env` and configure:
- FalkorDB connection settings
- OpenAI API key for embeddings
- Optional: PostgreSQL settings, API authentication key

## Architecture Overview

### Core Components
1. **Knowledge Graph**: Graphiti-core with bi-temporal data model for tracking facts and their validity periods
2. **Database**: FalkorDB for graph storage, optional PostgreSQL for additional data
3. **API**: FastAPI with async/await patterns, CORS support, optional API key authentication
4. **Ontology**: Custom entities (Person, Organization, Project) with Texas government-specific attributes

### Directory Structure
- `src/api/`: API endpoints (search functionality)
- `src/models/`: Data models including custom ontology definitions
- `src/db/`: Database connections and graph operations
- `src/config.py`: Pydantic-based configuration management
- `src/data/`: Static data files (fwtx.json, governance.md)
- `wiki.py`: Main application entry point

### Key Design Patterns
1. **Temporal Knowledge Graph**: All facts have valid_from/valid_until timestamps
2. **Texas Government Ontology**: Specialized for Texas municipal structures (e.g., home-rule cities, council-manager government)
3. **Entity Resolution**: Uses embeddings and similarity search for deduplication
4. **GraphRAG Pattern**: Combines graph traversal with LLM-based retrieval

## Important Context

### Texas Municipal Government Structure
The system models Texas-specific governance including:
- Home-rule cities (populations >5,000 with custom charters)
- Council-manager government form
- Texas Local Government Code compliance
- County/city jurisdictional boundaries

### Current Implementation Status
- Basic FastAPI structure is in place
- Custom ontology is defined in `src/models/ontology.py`
- FalkorDB integration is configured
- API endpoints are scaffolded but need implementation
- No testing infrastructure exists yet

### When Implementing Features
1. Follow the existing async/await patterns in FastAPI
2. Use the defined ontology models for consistency
3. Maintain temporal data integrity (valid_from/valid_until)
4. Consider Texas government structures when modeling data
5. Use Graphiti's built-in entity resolution for deduplication