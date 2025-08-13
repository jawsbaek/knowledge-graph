// Advanced Cypher 25 Queries for Knowledge Graph
// Reference: https://neo4j.com/docs/cypher-manual/25/introduction/

// Set Cypher version to 25 for all queries
CYPHER 25;

// ====================================================================
// 1. COLLECT Subqueries - Advanced Aggregation
// ====================================================================

// Get methodology with all practices and their rules in a single query
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
                        RETURN r {
                            .*,
                            evidence: [
                                COLLECT {
                                    MATCH (r)-[:SUPPORTED_BY]->(e:Evidence)
                                    RETURN e
                                }
                            ]
                        }
                    }
                ]
            }
        }
    ]
} as methodology_details;

// ====================================================================
// 2. EXISTS Subqueries - Complex Filtering
// ====================================================================

// Find rules that apply in remote team contexts
MATCH (r:Rule)
WHERE EXISTS {
    MATCH (r)-[:APPLIES_IN]->(c:Context)
    WHERE c.name = "Remote Team" 
    OR ANY(constraint IN c.constraints WHERE constraint CONTAINS "remote")
}
RETURN r.title, r.priority, r.category
ORDER BY r.priority DESC;

// Find methodologies that have practices with high-priority rules
MATCH (m:Methodology)
WHERE EXISTS {
    MATCH (m)-[:HAS_PRACTICE]->(p:Practice)-[:HAS_RULE]->(r:Rule)
    WHERE r.priority IN ["high", "critical"]
}
RETURN m.name, m.category;

// ====================================================================
// 3. COUNT Subqueries - Aggregation without Grouping
// ====================================================================

// Get methodologies with practice and rule counts
MATCH (m:Methodology)
RETURN m.name,
       COUNT { (m)-[:HAS_PRACTICE]->() } as practice_count,
       COUNT { (m)-[:HAS_PRACTICE]->()-[:HAS_RULE]->() } as total_rules
ORDER BY total_rules DESC;

// ====================================================================
// 4. Conditional Queries with WHEN
// ====================================================================

// Conditionally include rules based on priority level
WHEN $include_critical_only THEN
    MATCH (r:Rule {priority: "critical"})
    RETURN r.title, r.detail, "critical" as rule_set
ELSE
    MATCH (r:Rule)
    WHERE r.priority IN ["high", "critical"]
    RETURN r.title, r.detail, "high_and_critical" as rule_set;

// ====================================================================
// 5. Advanced Pattern Matching
// ====================================================================

// Find shortest path between methodologies through practices
MATCH path = shortestPath((m1:Methodology)-[:HAS_PRACTICE|RELATED_TO*]-(m2:Methodology))
WHERE m1.name = "Agile" AND m2.name = "DevOps"
RETURN path, length(path) as path_length;

// Variable-length pattern for finding all connected methodologies
MATCH (start:Methodology {name: "Scrum"})-[:HAS_PRACTICE|RELATED_TO*1..3]-(connected:Methodology)
WHERE start <> connected
RETURN DISTINCT connected.name, connected.category;

// ====================================================================
// 6. Complex Recommendation Queries
// ====================================================================

// Recommend methodologies based on context similarity
MATCH (target_context:Context {name: $context_name})
CALL {
    WITH target_context
    MATCH (similar_context:Context)
    WHERE similar_context <> target_context
    AND ANY(constraint IN similar_context.constraints 
            WHERE constraint IN target_context.constraints)
    
    MATCH (similar_context)<-[:APPLIES_IN]-(r:Rule)<-[:HAS_RULE]-(p:Practice)<-[:HAS_PRACTICE]-(m:Methodology)
    RETURN m, count(*) as similarity_score
    ORDER BY similarity_score DESC
    LIMIT 5
}
RETURN m.name, m.description, similarity_score;

// ====================================================================
// 7. Knowledge Graph Analysis
// ====================================================================

// Find the most influential practices (connected to most rules and contexts)
MATCH (p:Practice)
CALL {
    WITH p
    MATCH (p)-[:HAS_RULE]->(r:Rule)
    RETURN count(r) as rule_count
}
CALL {
    WITH p
    MATCH (p)-[:HAS_RULE]->(r:Rule)-[:APPLIES_IN]->(c:Context)
    RETURN count(DISTINCT c) as context_count
}
RETURN p.name, 
       rule_count, 
       context_count,
       (rule_count + context_count) as influence_score
ORDER BY influence_score DESC
LIMIT 10;

// ====================================================================
// 8. Evidence-Based Rule Discovery
// ====================================================================

// Find rules with the strongest evidence support
MATCH (r:Rule)
CALL {
    WITH r
    MATCH (r)-[:SUPPORTED_BY]->(e:Evidence)
    RETURN avg(e.credibility_score) as avg_credibility,
           count(e) as evidence_count
}
WHERE evidence_count > 0
RETURN r.title, 
       r.priority,
       avg_credibility,
       evidence_count,
       (avg_credibility * evidence_count) as evidence_strength
ORDER BY evidence_strength DESC;

// ====================================================================
// 9. Temporal and Trending Analysis
// ====================================================================

// Find methodology adoption trends by year
MATCH (m:Methodology)
WHERE m.year_created IS NOT NULL
RETURN m.year_created as year,
       count(*) as methodologies_introduced,
       collect(m.name) as methodology_names
ORDER BY year;

// Find modern vs traditional methodology patterns
MATCH (modern:Methodology)
WHERE modern.year_created >= 2000
CALL {
    WITH modern
    MATCH (modern)-[:HAS_PRACTICE]->(p:Practice)-[:HAS_RULE]->(r:Rule)
    WHERE r.category IN ["automation", "collaboration", "continuous"]
    RETURN count(r) as modern_rule_count
}

MATCH (traditional:Methodology)
WHERE traditional.year_created < 2000
CALL {
    WITH traditional
    MATCH (traditional)-[:HAS_PRACTICE]->(p:Practice)-[:HAS_RULE]->(r:Rule)
    WHERE r.category IN ["documentation", "planning", "control"]
    RETURN count(r) as traditional_rule_count
}

RETURN "Modern methodologies focus on:" as insight,
       collect(DISTINCT modern.name) as modern_methodologies,
       sum(modern_rule_count) as total_modern_rules,
       "Traditional methodologies focus on:" as traditional_insight,
       collect(DISTINCT traditional.name) as traditional_methodologies,
       sum(traditional_rule_count) as total_traditional_rules;

// ====================================================================
// 10. Performance-Optimized Queries
// ====================================================================

// Use index hints for better performance
MATCH (m:Methodology)
USING INDEX m:Methodology(name)
WHERE m.name = $methodology_name
RETURN m;

// Parallel execution hint for large datasets
MATCH (r:Rule)
WHERE r.priority = "high"
CALL {
    WITH r
    MATCH (r)-[:APPLIES_IN]->(c:Context)
    RETURN c
} IN TRANSACTIONS OF 1000 ROWS
RETURN count(*) as high_priority_rule_contexts;

// ====================================================================
// 11. Graph Algorithm Patterns
// ====================================================================

// Find central methodologies using degree centrality concept
MATCH (m:Methodology)
CALL {
    WITH m
    MATCH (m)-[:HAS_PRACTICE|RELATED_TO]-(connected)
    RETURN count(connected) as degree
}
RETURN m.name, degree
ORDER BY degree DESC
LIMIT 5;

// Find methodology clusters
MATCH (m1:Methodology)-[:RELATED_TO]-(m2:Methodology)
WHERE id(m1) < id(m2)
CALL {
    WITH m1, m2
    MATCH path = (m1)-[:RELATED_TO*2..3]-(m2)
    RETURN count(path) as path_count
}
RETURN m1.name, m2.name, path_count
ORDER BY path_count DESC;

// ====================================================================
// 12. Data Quality and Validation
// ====================================================================

// Find orphaned nodes (not connected to the main graph)
MATCH (r:Rule)
WHERE NOT EXISTS { (r)<-[:HAS_RULE]-() }
RETURN r.title as orphaned_rules;

MATCH (e:Evidence)
WHERE NOT EXISTS { (e)<-[:SUPPORTED_BY]-() }
RETURN e.title as unused_evidence;

// Find incomplete methodologies (without practices)
MATCH (m:Methodology)
WHERE NOT EXISTS { (m)-[:HAS_PRACTICE]->() }
RETURN m.name as incomplete_methodologies;

// Validate rule priorities
MATCH (r:Rule)
WHERE r.priority NOT IN ["low", "medium", "high", "critical"]
RETURN r.name, r.priority as invalid_priority;

// ====================================================================
// 13. Export and Integration Queries
// ====================================================================

// Export methodology hierarchy for external tools
MATCH (m:Methodology)
OPTIONAL MATCH (m)-[:HAS_PRACTICE]->(p:Practice)
OPTIONAL MATCH (p)-[:HAS_RULE]->(r:Rule)
RETURN m.name as methodology,
       p.name as practice,
       r.title as rule,
       r.priority as rule_priority
ORDER BY methodology, practice, rule_priority DESC;

// Generate knowledge graph statistics
CALL {
    MATCH (:Methodology) 
    RETURN count(*) as methodology_count
}
CALL {
    MATCH (:Practice) 
    RETURN count(*) as practice_count
}
CALL {
    MATCH (:Rule) 
    RETURN count(*) as rule_count
}
CALL {
    MATCH (:Context) 
    RETURN count(*) as context_count
}
CALL {
    MATCH (:Evidence) 
    RETURN count(*) as evidence_count
}
RETURN methodology_count, practice_count, rule_count, context_count, evidence_count;
