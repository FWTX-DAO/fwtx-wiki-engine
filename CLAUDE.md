# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fort Worth Wiki is a knowledge graph-based system for Fort Worth municipal information using FastAPI, FalkorDB, and Graphiti-core with Google Gemini integration for GraphRAG (Graph Retrieval-Augmented Generation).

## Development Commands

### Setup and Running
```bash
# Install dependencies (requires Python 3.13+)
uv sync

# Start FalkorDB (required for knowledge graph)
docker run -p 6379:6379 -p 3000:3000 -it --rm falkordb/falkordb:latest

# Run the application
uv run wiki.py

# Alternative: run with auto-reload
uvicorn wiki:app --host 0.0.0.0 --port 8001 --reload

# Access the web interface
open http://localhost:8001
```

### Environment Configuration
Copy `.env.example` to `.env` and configure:
- `GOOGLE_API_KEY` (required for Gemini LLM/embeddings)
- FalkorDB connection settings (defaults to localhost:6379)
- Optional: PostgreSQL settings, API authentication key
- `ENABLE_SYNC_SCHEDULER` (set to "true" for automated data sync)
- `SYNC_INTERVAL_HOURS` (how often to sync data, default 24)
- Gemini model settings (GEMINI_MODEL, GEMINI_PRO_MODEL, GEMINI_EMBEDDING_MODEL)
- `LOAD_INITIAL_DATA` (set to "true" to load initial structured data)
- `SYNC_MODE` ("initial" for JSON data or "live" for AI research)

## Architecture Overview

### Core Components
1. **Knowledge Graph**: Graphiti-core with bi-temporal data model for tracking facts and their validity periods
2. **Database**: FalkorDB for graph storage (GraphBLAS sparse matrix implementation), optional PostgreSQL
3. **API**: FastAPI with async/await patterns, CORS support, optional API key authentication
4. **Ontology**: Texas Ontology Protocol (TOP) implementation with specialized entities
5. **AI Agents**: Agno-based research team using Gemini models for live data collection
6. **Web Client**: Interactive UI with Cytoscape.js graph visualization and chat interface
7. **Data Sync**: Automated scheduler for periodic data updates using AI agents

### Directory Structure
- `src/api/`: API endpoints (chat, sync, research)
- `src/models/`: Data models including TOP implementation
  - `src/models/top/`: Texas Ontology Protocol modules
- `src/db/`: Database connections and graph operations
- `src/services/`: Core services
  - `src/services/agent/`: AI research agents using Agno
  - `src/services/sync/`: Data synchronization and scheduling
  - `src/services/graphiti/`: Knowledge graph operations
- `src/config.py`: Pydantic-based configuration management
- `src/data/`: Static data files (fwtx.json with service URLs, governance.md with government structure)
- `client/`: Web UI with graph visualization and chat
- `wiki.py`: Main application entry point

### Key Design Patterns
1. **Temporal Knowledge Graph**: All facts have valid_from/valid_until timestamps
2. **Texas Government Ontology**: Specialized for Texas municipal structures (home-rule cities, council-manager government)
3. **Entity Resolution**: Uses embeddings and similarity search for deduplication
4. **GraphRAG Pattern**: Combines graph traversal with LLM-based retrieval
5. **Episode-Based Updates**: Tracks data source updates with temporal context

## Important Context

### Texas Municipal Government Structure
The system models Texas-specific governance including:
- Home-rule cities (populations >5,000 with custom charters)
- Council-manager government form
- Texas Local Government Code compliance
- County/city jurisdictional boundaries

### AI Research System
The system uses Agno-based AI agents powered by Google Gemini for data collection:
- **Web Research Agent**: Uses Gemini with grounding/search for accurate Fort Worth data
- **Data Structure Agent**: Converts data to TOP-compliant format using Gemini
- **County Integration Analyst**: Analyzes city-county relationships with Gemini Pro
- All agents leverage Gemini's grounding capabilities for factual accuracy

### Data Flow
1. User queries via chat interface or API
2. GraphRAG queries knowledge graph using Graphiti with Gemini embeddings
3. If data is missing, AI agents can research it
4. Scheduler periodically updates data from live sources
5. All data includes temporal validity and source attribution

### Current Implementation Status
- ✅ FastAPI structure with chat, sync, and research endpoints
- ✅ Texas Ontology Protocol (TOP) fully implemented in `src/models/top/`
- ✅ FalkorDB integration with Graphiti-core
- ✅ Chat API with GraphRAG capabilities
- ✅ AI research agents using Agno framework
- ✅ Web client with graph visualization and chat interface
- ✅ Automated data synchronization with APScheduler
- ✅ Live data fetching from web sources (no hardcoded data)
- 🔲 Testing infrastructure needs implementation
- 🔲 Multi-municipality support planned

### When Implementing Features
1. Follow the existing async/await patterns in FastAPI
2. Use the Texas Ontology Protocol (TOP) models for consistency
3. Maintain temporal data integrity (valid_from/valid_until)
4. Consider Texas government structures when modeling data
5. Use Graphiti's built-in entity resolution for deduplication
6. Leverage FalkorDB's sparse matrix architecture for performance
7. Use AI agents for live data fetching - NO hardcoded sample data
8. Follow the Agno pattern for new research agents
9. Ensure all data has proper source attribution and confidence levels