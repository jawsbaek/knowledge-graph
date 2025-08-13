# Knowledge Graph - Programming Methodology Management System

🧠 A graph-based knowledge management system for programming development methodologies using Neo4j, FastAPI, and Streamlit.

## Overview

This project implements a comprehensive knowledge graph system that manages programming development methodologies (Agile, Scrum, DevOps, etc.) and their associated practices, rules, contexts, and evidence. The system allows you to:

- **Manage methodologies** and their practices hierarchically
- **Define rules and guidelines** for specific practices
- **Create contexts** that define when certain rules apply
- **Link evidence** to support rules and practices
- **Visualize relationships** between different concepts
- **Query the knowledge graph** for recommendations and insights
- **Integrate external data** from sources like ThoughtWorks Technology Radar

## Architecture

```
[Streamlit UI] <-> [FastAPI API] <-> [Neo4j Database 2025.07.01]
                                           ↑
                               [Technology Radar Pipeline]
```

### Core Entities

- **Methodology**: Development approaches (Agile, Scrum, Waterfall, DevOps, Kanban)
- **Practice**: Specific activities within methodologies (Daily Scrum, Sprint Planning, CI/CD)
- **Rule**: Guidelines and best practices for each practice
- **Context**: Situations where rules apply (Remote Team, Startup, Enterprise)
- **Evidence**: Supporting documentation, papers, and references
- **RadarTechnique**: Technology trends from ThoughtWorks Technology Radar

### Relationships

- `Methodology -[:HAS_PRACTICE]-> Practice`
- `Practice -[:HAS_RULE]-> Rule`
- `Rule -[:APPLIES_IN]-> Context`
- `Rule -[:SUPPORTED_BY]-> Evidence`
- `RadarTechnique -[:INFLUENCES_PRACTICE]-> Practice`
- `Any -[:RELATED_TO]-> Any`

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Docker and Docker Compose
- Neo4j (can be run via Docker)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd knowledge-graph
   ```

2. **Install dependencies**
   ```bash
   uv sync --dev
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start the services with Docker Compose**
   ```bash
   cd docker
   docker-compose up -d
   ```

   This will start:
   - Neo4j database 2025.07.01 on `http://localhost:7474` (browser) and `bolt://localhost:7687`
   - FastAPI backend on `http://localhost:8000`
   - Streamlit UI on `http://localhost:8501`

### Manual Setup (Development)

1. **Start Neo4j**
   ```bash
   # Using Docker
   docker run -d \
     --name neo4j \
     -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/knowledge123 \
     -e NEO4J_PLUGINS='["apoc"]' \
     neo4j:2025.07.01
   ```

2. **Initialize sample data**
   ```bash
   uv run python scripts/init_sample_data.py
   ```
   
   Or load from Cypher script:
   ```bash
   # Copy the script to Neo4j import directory
   docker cp data/sample_data.cypher neo4j:/var/lib/neo4j/import/
   
   # Execute in Neo4j browser (http://localhost:7474)
   :play file:///sample_data.cypher
   ```

3. **Start the API server**
   ```bash
   uv run python -m knowledge_graph.api.main
   ```

4. **Start the Streamlit UI**
   ```bash
   uv run streamlit run src/knowledge_graph/ui/app.py
   ```

## Usage

### Web Interface

Access the Streamlit UI at `http://localhost:8501` to:

- **Dashboard**: Overview of methodologies, practices, rules, and contexts
- **Methodologies**: Create and manage development methodologies
- **Practices**: Define practices within methodologies
- **Rules**: Set up rules and guidelines for practices
- **Contexts**: Create situations where rules apply
- **Graph Visualization**: Explore the knowledge graph (future feature)

### API Interface

The FastAPI backend provides a REST API at `http://localhost:8000`:

- **Interactive Documentation**: `http://localhost:8000/docs`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`
- **Health Check**: `http://localhost:8000/health`

### Technology Radar Integration

Integrate external methodology data from ThoughtWorks Technology Radar:

```bash
# Ingest specific technique (e.g., Fuzz Testing)
uv run python scripts/run_radar_pipeline.py fuzz-testing

# Run demo pipeline with multiple techniques
uv run python scripts/run_radar_pipeline.py demo

# Ingest specific technique via API
curl -X POST "http://localhost:8000/api/v1/radar/ingest/technique/fuzz-testing"
```

### Example API Usage

```python
import httpx

# Get all methodologies
response = httpx.get("http://localhost:8000/api/v1/methodologies")
methodologies = response.json()

# Create a new methodology
methodology_data = {
    "name": "Extreme Programming",
    "description": "Agile software development framework",
    "origin": "Kent Beck",
    "year_created": 1996,
    "category": "Agile"
}
response = httpx.post("http://localhost:8000/api/v1/methodologies", json=methodology_data)

# Ingest Technology Radar technique
response = httpx.post("http://localhost:8000/api/v1/radar/ingest/technique/threat-modeling")
```

### Neo4j Cypher 25 Queries

Connect to Neo4j at `bolt://localhost:7687` with credentials `neo4j/knowledge123`.

This project uses **Cypher 25** syntax for enhanced performance and modern features. Reference: [Neo4j Cypher Manual 25](https://neo4j.com/docs/cypher-manual/25/introduction/)

#### Basic Queries
```cypher
// Set Cypher version (recommended for all queries)
CYPHER 25

// Find all practices for Agile methodology
MATCH (m:Methodology {name: "Agile"})-[:HAS_PRACTICE]->(p:Practice)
RETURN p.name, p.description

// Get rules that apply in remote team context
MATCH (c:Context {name: "Remote Team"})<-[:APPLIES_IN]-(r:Rule)
RETURN r.title, r.detail, r.priority
```

#### Advanced Cypher 25 Features
```cypher
// Use COLLECT subqueries for complex aggregations
MATCH (m:Methodology {name: "Scrum"})
RETURN m {
    .*,
    practices: [
        COLLECT {
            MATCH (m)-[:HAS_PRACTICE]->(p:Practice)
            RETURN p {
                .*,
                rules: [
                    COLLECT {
                        MATCH (p)-[:HAS_RULE]->(r:Rule)
                        RETURN r
                    }
                ]
            }
        }
    ]
}

// Use EXISTS for complex filtering
MATCH (r:Rule)
WHERE EXISTS {
    MATCH (r)-[:APPLIES_IN]->(c:Context)
    WHERE ANY(constraint IN c.constraints WHERE constraint CONTAINS "remote")
}
RETURN r.title, r.priority

// Use COUNT subqueries for metrics
MATCH (m:Methodology)
RETURN m.name,
       COUNT { (m)-[:HAS_PRACTICE]->() } as practice_count,
       COUNT { (m)-[:HAS_PRACTICE]->()-[:HAS_RULE]->() } as total_rules

// Query Technology Radar techniques
MATCH (rt:RadarTechnique)
WHERE rt.ring = "Adopt"
OPTIONAL MATCH (rt)-[:INFLUENCES_PRACTICE]->(p:Practice)
RETURN rt.name, rt.description, collect(p.name) as influenced_practices
```

See `data/cypher25_examples.cypher` for comprehensive examples of Cypher 25 features.

## Development

### Project Structure

```
knowledge-graph/
├── src/knowledge_graph/
│   ├── api/                    # FastAPI application
│   │   ├── main.py            # Main application
│   │   └── routers/           # API route handlers
│   ├── database/              # Neo4j connection and repositories
│   ├── models/                # Pydantic data models
│   ├── pipeline/              # External data integration
│   │   ├── scrapers/          # Web scrapers
│   │   ├── processors/        # Data processors
│   │   └── ingestors/         # Neo4j ingestors
│   ├── services/              # Business logic services
│   ├── ui/                    # Streamlit application
│   └── utils/                 # Utilities and configuration
├── tests/                     # Test suite
├── scripts/                   # Utility scripts
├── data/                      # Sample data and schemas
├── docker/                    # Docker configuration
└── docs/                      # Documentation
```

### Code Quality

The project uses several tools for code quality:

```bash
# Format code
uv run black src/ tests/

# Sort imports
uv run isort src/ tests/

# Type checking
uv run mypy src/

# Linting
uv run flake8 src/ tests/

# Run tests
uv run pytest
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `uv run pytest`
5. Run code quality checks: `uv run black . && uv run isort . && uv run mypy src/`
6. Commit your changes: `git commit -am 'Add feature'`
7. Push to the branch: `git push origin feature-name`
8. Create a Pull Request

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` |
| `NEO4J_USERNAME` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `knowledge123` |
| `NEO4J_DATABASE` | Neo4j database name | `neo4j` |
| `API_HOST` | API server host | `0.0.0.0` |
| `API_PORT` | API server port | `8000` |
| `DEBUG` | Enable debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Neo4j Configuration

The system requires Neo4j 2025.07.01 with APOC procedures enabled. The Docker setup automatically configures this.

For manual Neo4j setup:
1. Install APOC plugin
2. Enable unrestricted procedures: `dbms.security.procedures.unrestricted=apoc.*`
3. Configure memory settings based on your data size

## Sample Data

The system includes comprehensive sample data covering:

- **5 Methodologies**: Agile, Scrum, Waterfall, DevOps, Kanban
- **9 Practices**: User Stories, Sprint Planning, Daily Scrum, CI/CD, etc.
- **7 Rules**: Time-boxing, INVEST criteria, automated testing, etc.
- **4 Contexts**: Remote Team, Startup, Enterprise, Open Source
- **4 Evidence sources**: Agile Manifesto, Scrum Guide, DevOps Handbook, etc.
- **Technology Radar Integration**: Fuzz Testing, Threat Modeling, etc.

## External Data Sources

### ThoughtWorks Technology Radar

The system can automatically ingest data from [ThoughtWorks Technology Radar](https://www.thoughtworks.com/radar):

- **Techniques**: Software development practices and approaches
- **Tools**: Development and operational tools
- **Platforms**: Infrastructure and platform technologies
- **Languages & Frameworks**: Programming languages and frameworks

Each radar item includes:
- **Ring**: Adoption recommendation (Adopt, Trial, Assess, Hold)
- **Quadrant**: Technology category
- **Movement**: Change indicator
- **Description**: Detailed explanation
- **Related items**: Connected technologies

### Knowledge Sources

- **PMI (Project Management Institute)**: https://www.pmi.org - PMBOK Guide and methodology frameworks
- **Agile Alliance**: https://www.agilealliance.org - Agile principles and practices
- **Scrum Guides**: https://scrumguides.org - Official Scrum methodology documentation
- **SEBoK**: https://www.sebokwiki.org - Systems Engineering Body of Knowledge
- **ThoughtWorks Technology Radar**: https://www.thoughtworks.com/radar - Technology trends and recommendations

## Extending the System

### Adding New Node Types

1. Define Pydantic models in `src/knowledge_graph/models/`
2. Create repository class in `src/knowledge_graph/database/repository.py`
3. Add API endpoints in `src/knowledge_graph/api/routers/`
4. Update UI in `src/knowledge_graph/ui/app.py`

### Custom Relationships

Add new relationship types by:
1. Updating repository methods
2. Adding API endpoints for relationship management
3. Updating the UI to visualize new relationships

### Data Pipeline Integration

Extend the pipeline system for new data sources:
1. Create scraper in `src/knowledge_graph/pipeline/scrapers/`
2. Add processor in `src/knowledge_graph/pipeline/processors/`
3. Implement ingestor in `src/knowledge_graph/pipeline/ingestors/`
4. Add orchestration logic

### Advanced Queries

Leverage Neo4j's graph algorithms and APOC procedures for:
- Shortest path between concepts
- Community detection in methodology clusters
- Centrality analysis for important practices
- Recommendation algorithms based on context similarity

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Neo4j 2025.07.01](https://hub.docker.com/_/neo4j) for the advanced graph database
- [FastAPI](https://fastapi.tiangolo.com/) for the high-performance API framework
- [Streamlit](https://streamlit.io/) for the rapid UI development
- [ThoughtWorks Technology Radar](https://www.thoughtworks.com/radar) for technology trend insights
- Knowledge sources: Agile Alliance, Scrum.org, DevOps community