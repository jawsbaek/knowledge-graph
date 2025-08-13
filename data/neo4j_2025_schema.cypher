// Neo4j 2025.07.01 Optimized Schema for Knowledge Graph
// Using advanced Cypher 25 features and Neo4j 2025 capabilities
// Reference: https://hub.docker.com/_/neo4j

// Select Cypher 25 for all operations
CYPHER 25;

// ====================================================================
// Create Advanced Indexes for Neo4j 2025.07.01
// ====================================================================

// Primary unique constraints with enhanced performance
CREATE CONSTRAINT methodology_name_unique FOR (m:Methodology) REQUIRE m.name IS UNIQUE;
CREATE CONSTRAINT practice_name_unique FOR (p:Practice) REQUIRE p.name IS UNIQUE;
CREATE CONSTRAINT rule_name_unique FOR (r:Rule) REQUIRE r.name IS UNIQUE;
CREATE CONSTRAINT context_name_unique FOR (c:Context) REQUIRE c.name IS UNIQUE;
CREATE CONSTRAINT evidence_name_unique FOR (e:Evidence) REQUIRE e.name IS UNIQUE;

// Technology Radar specific constraints
CREATE CONSTRAINT radar_technique_name_unique FOR (rt:RadarTechnique) REQUIRE rt.name IS UNIQUE;

// Enhanced composite indexes for Neo4j 2025
CREATE INDEX methodology_category_year FOR (m:Methodology) ON (m.category, m.year_created);
CREATE INDEX rule_priority_category FOR (r:Rule) ON (r.priority, r.category);
CREATE INDEX context_team_industry FOR (c:Context) ON (c.team_size, c.industry);
CREATE INDEX evidence_credibility FOR (e:Evidence) ON (e.credibility_score, e.source_type);

// Technology Radar specific indexes
CREATE INDEX radar_ring_quadrant FOR (rt:RadarTechnique) ON (rt.ring, rt.quadrant);
CREATE INDEX radar_volume_date FOR (rt:RadarTechnique) ON (rt.volume, rt.edition_date);
CREATE INDEX radar_movement FOR (rt:RadarTechnique) ON (rt.movement);

// Full-text search indexes for Neo4j 2025
CREATE FULLTEXT INDEX methodology_search FOR (m:Methodology) ON EACH [m.name, m.description];
CREATE FULLTEXT INDEX practice_search FOR (p:Practice) ON EACH [p.name, p.description];
CREATE FULLTEXT INDEX rule_search FOR (r:Rule) ON EACH [r.title, r.detail];
CREATE FULLTEXT INDEX radar_search FOR (rt:RadarTechnique) ON EACH [rt.name, rt.description];

// ====================================================================
// Vector Indexes for AI/ML Integration (Neo4j 2025 Feature)
// ====================================================================

// Methodology embeddings for semantic similarity
CREATE VECTOR INDEX methodology_embeddings
FOR (m:Methodology) ON (m.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// Practice embeddings for recommendation systems
CREATE VECTOR INDEX practice_embeddings  
FOR (p:Practice) ON (p.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// Rule embeddings for contextual matching
CREATE VECTOR INDEX rule_embeddings
FOR (r:Rule) ON (r.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// Technology Radar embeddings for trend analysis
CREATE VECTOR INDEX radar_embeddings
FOR (rt:RadarTechnique) ON (rt.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// ====================================================================
// Advanced Node Labels and Properties (Neo4j 2025)
// ====================================================================

// Add temporal properties for change tracking
MATCH (m:Methodology)
SET m.created_at = coalesce(m.created_at, datetime()),
    m.updated_at = datetime(),
    m.version = coalesce(m.version, 1);

MATCH (p:Practice)  
SET p.created_at = coalesce(p.created_at, datetime()),
    p.updated_at = datetime(),
    p.version = coalesce(p.version, 1);

MATCH (r:Rule)
SET r.created_at = coalesce(r.created_at, datetime()),
    r.updated_at = datetime(),
    r.version = coalesce(r.version, 1);

// Add Technology Radar temporal tracking
MATCH (rt:RadarTechnique)
SET rt.created_at = coalesce(rt.created_at, datetime()),
    rt.updated_at = datetime(),
    rt.last_radar_update = datetime();

// ====================================================================
// Advanced Relationship Types for Neo4j 2025
// ====================================================================

// Weighted relationships for recommendation algorithms
MATCH (m:Methodology)-[r:HAS_PRACTICE]->(p:Practice)
SET r.weight = coalesce(r.weight, 1.0),
    r.created_at = coalesce(r.created_at, datetime());

MATCH (p:Practice)-[r:HAS_RULE]->(rule:Rule)
SET r.weight = coalesce(r.weight, 1.0),
    r.created_at = coalesce(r.created_at, datetime());

// Technology Radar influence relationships
MATCH (rt:RadarTechnique)-[r:INFLUENCES_PRACTICE]->(p:Practice)
SET r.influence_score = coalesce(r.influence_score, 
    CASE rt.ring 
        WHEN 'Adopt' THEN 0.9
        WHEN 'Trial' THEN 0.7
        WHEN 'Assess' THEN 0.5
        ELSE 0.3
    END),
    r.created_at = coalesce(r.created_at, datetime());

// ====================================================================
// Performance Optimization Queries (Neo4j 2025)
// ====================================================================

// Create statistics for query planner optimization
CALL db.stats.retrieve('GRAPH COUNTS');

// Memory configuration recommendations for Neo4j 2025
// These should be set in neo4j.conf:
// dbms.memory.heap.initial_size=1G
// dbms.memory.heap.max_size=2G  
// dbms.memory.pagecache.size=1G
// db.memory.transaction.total.max=1G

// ====================================================================
// Data Quality Constraints (Neo4j 2025)
// ====================================================================

// Ensure rule priorities are valid
CREATE CONSTRAINT rule_priority_valid 
FOR (r:Rule) REQUIRE r.priority IN ['low', 'medium', 'high', 'critical'];

// Ensure radar rings are valid
CREATE CONSTRAINT radar_ring_valid
FOR (rt:RadarTechnique) REQUIRE rt.ring IN ['Adopt', 'Trial', 'Assess', 'Hold'];

// Ensure radar quadrants are valid  
CREATE CONSTRAINT radar_quadrant_valid
FOR (rt:RadarTechnique) REQUIRE rt.quadrant IN ['Techniques', 'Tools', 'Platforms', 'Languages & Frameworks'];

// Ensure credibility scores are in valid range
CREATE CONSTRAINT evidence_credibility_range
FOR (e:Evidence) REQUIRE e.credibility_score >= 0.0 AND e.credibility_score <= 10.0;

// ====================================================================
// Monitoring and Analytics Setup (Neo4j 2025)
// ====================================================================

// Create monitoring nodes for system health
CREATE (monitor:SystemMonitor {
    name: 'Knowledge Graph Monitor',
    created_at: datetime(),
    neo4j_version: '2025.07.01',
    cypher_version: '25',
    last_health_check: datetime()
});

// Performance tracking for key operations
CREATE INDEX performance_tracking FOR (op:Operation) ON (op.operation_type, op.timestamp);

SHOW INDEXES;
