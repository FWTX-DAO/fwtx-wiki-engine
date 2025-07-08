# Fort Worth Wiki

The intent of this project is to provide a greenfield oppotunity to come into the information age with a wiki style experience but using state of the art information retrieval with Knowledge Graph Retrieval Augmented Generation (GraphRAG), and AI Agents for a intuitve and seamless ability to learn and find Fort Worth Public Services information.

## Tech Stack
- Graphiti
- FalkorDB
- Python 3.13
- OpenAI API (Subject to change or privacy)

## Dependencies
- uv (Recommended) for Python Virtual Environment and package management
- Docker (Recommended) for FalkorDB

## Setup

1. Clone the repository
`git clone https://github.com/FWTX-DAO/wiki.git`
2. Install dependencies (Recommended with uv for pyenv)
`uv sync`
3. Set up FalkorDB with Docker
`docker run -p 6379:6379 -p 3000:3000 -it --rm falkordb/falkordb:latest`
4. Run the script
`uv run wiki.py`
