# Fort Worth Municipal Knowledge Graph Quick Start Guide

## Project Structure

```
fwtx-wiki/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── ontology.py          # (existing - can deprecate)
│   │   └── municipal_schema.py  # Core municipal schema (new)
│   ├── episodes/
│   │   ├── __init__.py
│   │   ├── episodes.py          # (existing - can deprecate)
│   │   └── episodes_municipal.py # Municipal episodes (new)
│   ├── queries/
│   │   ├── __init__.py
│   │   └── municipal_queries.py # Query helpers (new)
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── json_processor.py   # Process fwtx.json
│   │   ├── pdf_processor.py    # Meeting minutes
│   │   └── gis_processor.py    # District boundaries
│   └── data/
│       ├── fwtx.json           # (existing)
│       └── governance.md       # (existing)
├── wiki.py                     # Main entry point (updated)
├── .env                        # Environment variables
├── pyproject.toml             # (existing)
└── README.md                  # (update with new features)
```

## Step 1: Install Schema Files

Create `src/models/municipal_schema.py` with the complete schema from the first artifact.

## Step 2: Create Episodes Module

Create `src/episodes/episodes_municipal.py` with the episode handling code from the second artifact.

## Step 3: Update wiki.py

Replace your existing `wiki.py` with the integrated version from the third artifact.

## Step 4: Initialize the Knowledge Graph

```bash
# First run - initialize indices
python wiki.py --init

# This will:
# 1. Create FalkorDB indices and constraints
# 2. Load Fort Worth government structure
# 3. Import data from fwtx.json
# 4. Set up initial relationships
```

## Step 5: Test Basic Queries

```bash
# Interactive mode
python wiki.py --interactive

# Single query
python wiki.py --query "Who is the mayor of Fort Worth?"

# District lookup
python wiki.py --district "123 Main Street, Fort Worth, TX"

# Service finder
python wiki.py --service "report a pothole"
```

## Key Implementation Phases

### Phase 1: Basic Structure (Week 1)
- [x] Core schema implementation
- [x] Government organization entities
- [x] Current office holders
- [x] Basic district information
- [ ] Test queries and validation

### Phase 2: Temporal Data (Week 2)
- [ ] Historical office holders
- [ ] Term tracking
- [ ] Election cycles
- [ ] Boundary change history

### Phase 3: Service Integration (Week 3)
- [ ] Department information
- [ ] 311 service categories
- [ ] Meeting schedules
- [ ] Public services directory

### Phase 4: Advanced Features (Week 4+)
- [ ] Committee memberships
- [ ] Voting records
- [ ] Campaign finance (if available)
- [ ] GIS boundary integration

## Data Sources Integration

### Immediate Sources
1. **fwtx.json** - Already parsed in the integration
2. **governance.md** - Extract structured data about current leadership
3. **Fort Worth Open Data Portal** - data.fortworthtexas.gov
4. **Meeting Agendas** - fortworthtexas.gov/citysecretary

### Future Sources
1. **Texas Ethics Commission** - Campaign finance data
2. **Tarrant Appraisal District** - Property boundaries
3. **Secretary of State** - Election results
4. **City GIS Services** - District shapefiles

## Query Examples

### Citizen Queries
```python
# Find my representative
"Who represents District 3 on Fort Worth City Council?"

# Get contact info
"How do I contact the mayor's office?"

# Find services
"How do I report a water main break?"

# Meeting info
"When does the city council meet?"
```

### Administrative Queries
```python
# Historical data
"Who held the mayor position before Mattie Parker?"

# Voting patterns
"How did council vote on the 2024 budget?"

# Committee info
"Who serves on the Planning Commission?"

# District changes
"When were Fort Worth districts last redrawn?"
```

## Performance Optimization

### FalkorDB Configuration
```python
# In your connection setup
falkor_driver = FalkorDriver(
    host='localhost',
    port='6379',
    max_connections=10,        # Connection pool
    query_timeout=5000,        # 5 second timeout
    enable_cache=True          # Query result caching
)
```

### Indexing Strategy
```cypher
// Create indices for common queries
CREATE INDEX ON :Person(full_name)
CREATE INDEX ON :District(identifier)
CREATE INDEX ON :Position(title)
CREATE INDEX ON :Meeting(scheduled_time)
```

## Deployment Considerations

### For Development
```bash
# Local FalkorDB
docker run -p 6379:6379 -p 3000:3000 -it --rm falkordb/falkordb:latest

# Environment variables
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
OPENAI_API_KEY=your_key_here
```

### For Production
```bash
# Use FalkorDB Cloud or dedicated instance
FALKORDB_HOST=your-instance.falkordb.com
FALKORDB_PORT=6379
FALKORDB_PASSWORD=secure_password

# Consider using alternative LLMs for privacy
# ANTHROPIC_API_KEY=... or local models
```

## Privacy and Security

### Citizen Data Protection
- No personal voter information
- Public records only
- Official sources only
- No private addresses

### API Security
```python
# Rate limiting for public access
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: get_remote_address(),
    default_limits=["100 per hour", "1000 per day"]
)
```

## Contributing to City Use

### Documentation Package
1. Technical documentation (this schema)
2. Data dictionary
3. Query examples
4. API documentation
5. Deployment guide

### Presentation Materials
1. Benefits overview (transparency, efficiency)
2. Cost analysis (infrastructure, maintenance)
3. Security/privacy compliance
4. Integration roadmap
5. Success metrics

## Next Steps

1. **Test Core Functionality**
   ```bash
   python wiki.py --interactive
   ```

2. **Validate Data Quality**
   - Check entity relationships
   - Verify temporal consistency
   - Test boundary queries

3. **Expand Data Sources**
   - Add more departments
   - Import historical data
   - Integrate real-time feeds

4. **Build API Layer**
   - RESTful endpoints
   - GraphQL interface
   - Authentication system

5. **Create UI/UX**
   - Citizen portal
   - Admin dashboard
   - Mobile app

## Support and Resources

- **Graphiti Docs**: [help.getzep.com/graphiti](https://help.getzep.com/graphiti)
- **FalkorDB Docs**: [docs.falkordb.com](https://docs.falkordb.com)
- **Schema.org Gov**: [schema.org/GovernmentOrganization](https://schema.org/GovernmentOrganization)
- **Open Civic Data**: [opencivicdata.org](https://opencivicdata.org)

## Monitoring and Maintenance

```python
# Add logging for queries
async def log_query(query: str, results_count: int, response_time: float):
    logger.info(f"Query: {query[:50]}... | Results: {results_count} | Time: {response_time:.2f}s")

# Regular data validation
async def validate_data_integrity():
    # Check for orphaned nodes
    # Verify relationship consistency
    # Validate temporal constraints
    pass
```

Remember: Start simple, validate often, and expand gradually. The schema is designed to grow with your needs while maintaining data integrity and query performance.
