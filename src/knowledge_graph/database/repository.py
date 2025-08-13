"""Repository classes for Neo4j database operations using Cypher 25.

This module implements repository patterns for Neo4j using Cypher 25 syntax.
Reference: https://neo4j.com/docs/cypher-manual/25/introduction/
"""

from typing import Any, Dict, List, Optional

from loguru import logger

from ..models.nodes import (
    Context, ContextCreate,
    Evidence, EvidenceCreate,
    Methodology, MethodologyCreate,
    Practice, PracticeCreate,
    Rule, RuleCreate,
)
from .connection import Neo4jConnection


class BaseRepository:
    """Base repository class for common database operations."""
    
    def __init__(self, connection: Neo4jConnection):
        """Initialize repository with database connection.
        
        Args:
            connection: Neo4j connection instance
        """
        self.connection = connection
    
    def _dict_to_node_properties(self, data: Dict[str, Any]) -> str:
        """Convert dictionary to Cypher node properties string.
        
        Args:
            data: Dictionary of node properties
            
        Returns:
            Cypher properties string
        """
        # Filter out None values and convert to Cypher format
        props = {k: v for k, v in data.items() if v is not None}
        return ", ".join([f"{k}: ${k}" for k in props.keys()])


class MethodologyRepository(BaseRepository):
    """Repository for Methodology nodes."""
    
    def create(self, methodology: MethodologyCreate) -> Methodology:
        """Create a new methodology node using Cypher 25.
        
        Args:
            methodology: Methodology data
            
        Returns:
            Created methodology
        """
        query = """
        CYPHER 25
        CREATE (m:Methodology {name: $name, description: $description, origin: $origin, 
                               year_created: $year_created, category: $category})
        RETURN m
        """
        
        result = self.connection.execute_write_query(
            query, methodology.model_dump(exclude_none=True)
        )
        
        if result:
            node_data = result[0]["m"]
            return Methodology(**node_data)
        
        raise RuntimeError("Failed to create methodology")
    
    def get_by_name(self, name: str) -> Optional[Methodology]:
        """Get methodology by name.
        
        Args:
            name: Methodology name
            
        Returns:
            Methodology or None if not found
        """
        query = "MATCH (m:Methodology {name: $name}) RETURN m"
        result = self.connection.execute_read_query(query, {"name": name})
        
        if result:
            node_data = result[0]["m"]
            return Methodology(**node_data)
        
        return None
    
    def get_all(self) -> List[Methodology]:
        """Get all methodologies.
        
        Returns:
            List of all methodologies
        """
        query = "MATCH (m:Methodology) RETURN m ORDER BY m.name"
        result = self.connection.execute_read_query(query)
        
        return [Methodology(**record["m"]) for record in result]
    
    def delete(self, name: str) -> bool:
        """Delete methodology by name.
        
        Args:
            name: Methodology name
            
        Returns:
            True if deleted, False if not found
        """
        query = """
        MATCH (m:Methodology {name: $name})
        DETACH DELETE m
        RETURN count(m) as deleted_count
        """
        
        result = self.connection.execute_write_query(query, {"name": name})
        return result[0]["deleted_count"] > 0 if result else False
    
    def find_related_methodologies(self, methodology_name: str, limit: int = 5) -> List[Methodology]:
        """Find methodologies related to the given one using Cypher 25 COLLECT subqueries.
        
        Args:
            methodology_name: Name of the source methodology
            limit: Maximum number of related methodologies to return
            
        Returns:
            List of related methodologies
        """
        query = """
        CYPHER 25
        MATCH (source:Methodology {name: $methodology_name})
        CALL {
            WITH source
            MATCH (source)-[:RELATED_TO|HAS_PRACTICE*..]-(related:Methodology)
            WHERE related <> source
            RETURN related, count(*) as connections
            ORDER BY connections DESC
            LIMIT $limit
        }
        RETURN related
        """
        
        result = self.connection.execute_read_query(
            query, {"methodology_name": methodology_name, "limit": limit}
        )
        return [Methodology(**record["related"]) for record in result]
    
    def get_with_practices_and_rules(self, methodology_name: str) -> Dict[str, Any]:
        """Get methodology with all its practices and rules using Cypher 25 COLLECT subqueries.
        
        Args:
            methodology_name: Name of the methodology
            
        Returns:
            Dictionary containing methodology, practices, and rules
        """
        query = """
        CYPHER 25
        MATCH (m:Methodology {name: $methodology_name})
        RETURN m,
        [
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
        ] as practices
        """
        
        result = self.connection.execute_read_query(query, {"methodology_name": methodology_name})
        if result:
            return {
                "methodology": Methodology(**result[0]["m"]),
                "practices": result[0]["practices"]
            }
        return {}


class PracticeRepository(BaseRepository):
    """Repository for Practice nodes."""
    
    def create(self, practice: PracticeCreate) -> Practice:
        """Create a new practice node and link to methodology.
        
        Args:
            practice: Practice data
            
        Returns:
            Created practice
        """
        query = """
        MATCH (m:Methodology {name: $methodology_name})
        CREATE (p:Practice {name: $name, description: $description, tools: $tools, 
                           difficulty_level: $difficulty_level, estimated_time: $estimated_time})
        CREATE (m)-[:HAS_PRACTICE]->(p)
        RETURN p
        """
        
        result = self.connection.execute_write_query(
            query, practice.model_dump(exclude_none=True)
        )
        
        if result:
            node_data = result[0]["p"]
            return Practice(**node_data)
        
        raise RuntimeError("Failed to create practice")
    
    def get_by_name(self, name: str) -> Optional[Practice]:
        """Get practice by name.
        
        Args:
            name: Practice name
            
        Returns:
            Practice or None if not found
        """
        query = "MATCH (p:Practice {name: $name}) RETURN p"
        result = self.connection.execute_read_query(query, {"name": name})
        
        if result:
            node_data = result[0]["p"]
            return Practice(**node_data)
        
        return None
    
    def get_by_methodology(self, methodology_name: str) -> List[Practice]:
        """Get practices by methodology name.
        
        Args:
            methodology_name: Methodology name
            
        Returns:
            List of practices for the methodology
        """
        query = """
        MATCH (m:Methodology {name: $methodology_name})-[:HAS_PRACTICE]->(p:Practice)
        RETURN p ORDER BY p.name
        """
        
        result = self.connection.execute_read_query(query, {"methodology_name": methodology_name})
        return [Practice(**record["p"]) for record in result]


class RuleRepository(BaseRepository):
    """Repository for Rule nodes."""
    
    def create(self, rule: RuleCreate) -> Rule:
        """Create a new rule node and link to practice.
        
        Args:
            rule: Rule data
            
        Returns:
            Created rule
        """
        query = """
        MATCH (p:Practice {name: $practice_name})
        CREATE (r:Rule {name: $name, title: $title, detail: $detail, priority: $priority, 
                       category: $category, tags: $tags})
        CREATE (p)-[:HAS_RULE]->(r)
        RETURN r
        """
        
        result = self.connection.execute_write_query(
            query, rule.model_dump(exclude_none=True)
        )
        
        if result:
            node_data = result[0]["r"]
            return Rule(**node_data)
        
        raise RuntimeError("Failed to create rule")
    
    def get_by_practice(self, practice_name: str) -> List[Rule]:
        """Get rules by practice name.
        
        Args:
            practice_name: Practice name
            
        Returns:
            List of rules for the practice
        """
        query = """
        MATCH (p:Practice {name: $practice_name})-[:HAS_RULE]->(r:Rule)
        RETURN r ORDER BY r.priority DESC, r.name
        """
        
        result = self.connection.execute_read_query(query, {"practice_name": practice_name})
        return [Rule(**record["r"]) for record in result]
    
    def get_by_context(self, context_name: str) -> List[Rule]:
        """Get rules applicable in a specific context.
        
        Args:
            context_name: Context name
            
        Returns:
            List of applicable rules
        """
        query = """
        MATCH (c:Context {name: $context_name})<-[:APPLIES_IN]-(r:Rule)
        RETURN r ORDER BY r.priority DESC, r.name
        """
        
        result = self.connection.execute_read_query(query, {"context_name": context_name})
        return [Rule(**record["r"]) for record in result]
    
    def get_rules_with_evidence(self, practice_name: str) -> List[Dict[str, Any]]:
        """Get rules with their supporting evidence using Cypher 25 COLLECT subqueries.
        
        Args:
            practice_name: Practice name
            
        Returns:
            List of rules with evidence
        """
        query = """
        CYPHER 25
        MATCH (p:Practice {name: $practice_name})-[:HAS_RULE]->(r:Rule)
        RETURN r {
            .*,
            evidence: [
                COLLECT {
                    MATCH (r)-[:SUPPORTED_BY]->(e:Evidence)
                    RETURN e
                }
            ]
        } as rule_with_evidence
        ORDER BY r.priority DESC, r.name
        """
        
        result = self.connection.execute_read_query(query, {"practice_name": practice_name})
        return [record["rule_with_evidence"] for record in result]
    
    def find_applicable_rules(self, context_constraints: List[str], team_size: str = None) -> List[Rule]:
        """Find rules applicable based on context constraints using Cypher 25 EXISTS.
        
        Args:
            context_constraints: List of constraints
            team_size: Optional team size filter
            
        Returns:
            List of applicable rules
        """
        query = """
        CYPHER 25
        MATCH (r:Rule)
        WHERE EXISTS {
            MATCH (r)-[:APPLIES_IN]->(c:Context)
            WHERE ANY(constraint IN c.constraints WHERE constraint IN $constraints)
            AND ($team_size IS NULL OR c.team_size = $team_size)
        }
        RETURN r
        ORDER BY r.priority DESC, r.name
        """
        
        params = {
            "constraints": context_constraints,
            "team_size": team_size
        }
        
        result = self.connection.execute_read_query(query, params)
        return [Rule(**record["r"]) for record in result]


class ContextRepository(BaseRepository):
    """Repository for Context nodes."""
    
    def create(self, context: ContextCreate) -> Context:
        """Create a new context node.
        
        Args:
            context: Context data
            
        Returns:
            Created context
        """
        query = """
        CREATE (c:Context {name: $name, description: $description, constraints: $constraints,
                          team_size: $team_size, project_type: $project_type, industry: $industry})
        RETURN c
        """
        
        result = self.connection.execute_write_query(
            query, context.model_dump(exclude_none=True)
        )
        
        if result:
            node_data = result[0]["c"]
            return Context(**node_data)
        
        raise RuntimeError("Failed to create context")
    
    def get_all(self) -> List[Context]:
        """Get all contexts.
        
        Returns:
            List of all contexts
        """
        query = "MATCH (c:Context) RETURN c ORDER BY c.name"
        result = self.connection.execute_read_query(query)
        
        return [Context(**record["c"]) for record in result]


class EvidenceRepository(BaseRepository):
    """Repository for Evidence nodes."""
    
    def create(self, evidence: EvidenceCreate) -> Evidence:
        """Create a new evidence node.
        
        Args:
            evidence: Evidence data
            
        Returns:
            Created evidence
        """
        query = """
        CREATE (e:Evidence {name: $name, title: $title, url: $url, summary: $summary,
                           source_type: $source_type, credibility_score: $credibility_score})
        RETURN e
        """
        
        result = self.connection.execute_write_query(
            query, evidence.model_dump(exclude_none=True)
        )
        
        if result:
            node_data = result[0]["e"]
            return Evidence(**node_data)
        
        raise RuntimeError("Failed to create evidence")
    
    def link_to_rule(self, evidence_name: str, rule_name: str) -> bool:
        """Link evidence to a rule.
        
        Args:
            evidence_name: Evidence name
            rule_name: Rule name
            
        Returns:
            True if linked successfully
        """
        query = """
        MATCH (e:Evidence {name: $evidence_name}), (r:Rule {name: $rule_name})
        CREATE (r)-[:SUPPORTED_BY]->(e)
        RETURN count(*) as created
        """
        
        result = self.connection.execute_write_query(
            query, {"evidence_name": evidence_name, "rule_name": rule_name}
        )
        
        return result[0]["created"] > 0 if result else False
