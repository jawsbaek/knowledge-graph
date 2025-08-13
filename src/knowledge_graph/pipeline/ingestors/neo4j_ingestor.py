"""Neo4j data ingestor for Technology Radar data."""

from typing import Any, Dict, List

from loguru import logger

from ...database import (
    ContextRepository,
    EvidenceRepository, 
    MethodologyRepository,
    PracticeRepository,
    RuleRepository,
    get_neo4j_connection,
)
from ...models.nodes import (
    ContextCreate,
    EvidenceCreate,
    MethodologyCreate,
    PracticeCreate,
    RuleCreate,
)
from ...models.radar import RadarItem, RadarTechnique


class Neo4jRadarIngestor:
    """Ingestor for Technology Radar data into Neo4j using Cypher 25."""
    
    def __init__(self):
        """Initialize the ingestor with repository connections."""
        self.connection = get_neo4j_connection()
        self.methodology_repo = MethodologyRepository(self.connection)
        self.practice_repo = PracticeRepository(self.connection)
        self.rule_repo = RuleRepository(self.connection)
        self.evidence_repo = EvidenceRepository(self.connection)
    
    def ingest_processed_data(self, processed_data: Dict[str, List]) -> Dict[str, int]:
        """Ingest processed Technology Radar data into Neo4j.
        
        Args:
            processed_data: Dictionary with lists of entities to create
            
        Returns:
            Dictionary with counts of created entities
        """
        results = {
            "methodologies_created": 0,
            "practices_created": 0,
            "rules_created": 0,
            "evidence_created": 0,
            "connections_created": 0,
            "errors": []
        }
        
        # Create methodologies
        for methodology_data in processed_data.get("methodologies", []):
            try:
                if not self.methodology_repo.get_by_name(methodology_data.name):
                    self.methodology_repo.create(methodology_data)
                    results["methodologies_created"] += 1
                    logger.info(f"Created methodology: {methodology_data.name}")
                else:
                    logger.debug(f"Methodology already exists: {methodology_data.name}")
            except Exception as e:
                error_msg = f"Failed to create methodology {methodology_data.name}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        # Create practices
        for practice_data in processed_data.get("practices", []):
            try:
                if not self.practice_repo.get_by_name(practice_data.name):
                    self.practice_repo.create(practice_data)
                    results["practices_created"] += 1
                    logger.info(f"Created practice: {practice_data.name}")
                else:
                    logger.debug(f"Practice already exists: {practice_data.name}")
            except Exception as e:
                error_msg = f"Failed to create practice {practice_data.name}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        # Create rules
        for rule_data in processed_data.get("rules", []):
            try:
                # Check if rule exists by name
                existing_rules = self.rule_repo.get_by_practice(rule_data.practice_name)
                if not any(r.name == rule_data.name for r in existing_rules):
                    self.rule_repo.create(rule_data)
                    results["rules_created"] += 1
                    logger.info(f"Created rule: {rule_data.title}")
                else:
                    logger.debug(f"Rule already exists: {rule_data.title}")
            except Exception as e:
                error_msg = f"Failed to create rule {rule_data.title}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        # Create evidence
        for evidence_data in processed_data.get("evidence", []):
            try:
                evidence_create = EvidenceCreate(**evidence_data)
                self.evidence_repo.create(evidence_create)
                results["evidence_created"] += 1
                logger.info(f"Created evidence: {evidence_create.title}")
            except Exception as e:
                error_msg = f"Failed to create evidence {evidence_data.get('title', 'Unknown')}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        # Create connections
        for connection in processed_data.get("connections", []):
            try:
                self._create_connection(connection)
                results["connections_created"] += 1
            except Exception as e:
                error_msg = f"Failed to create connection {connection}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        return results
    
    def ingest_radar_technique_direct(self, technique: RadarTechnique) -> Dict[str, Any]:
        """Directly ingest a radar technique as a specialized node.
        
        Args:
            technique: RadarTechnique to ingest
            
        Returns:
            Dictionary with ingestion results
        """
        try:
            # Create RadarTechnique node using Cypher 25
            query = """
            CYPHER 25
            MERGE (rt:RadarTechnique:TechRadar {name: $name})
            SET rt += {
                quadrant: $quadrant,
                ring: $ring,
                movement: $movement,
                description: $description,
                volume: $volume,
                edition_date: $edition_date,
                source_url: $source_url,
                created_at: datetime(),
                updated_at: datetime()
            }
            RETURN rt
            """
            
            params = {
                "name": technique.name,
                "quadrant": technique.quadrant.value,
                "ring": technique.ring.value,
                "movement": technique.movement.value,
                "description": technique.description,
                "volume": technique.volume,
                "edition_date": technique.edition_date,
                "source_url": str(technique.source_url) if technique.source_url else None
            }
            
            result = self.connection.execute_write_query(query, params)
            
            if result:
                logger.info(f"Created RadarTechnique node: {technique.name}")
                
                # Link to related practices if they exist
                self._link_radar_technique_to_practices(technique)
                
                return {
                    "success": True,
                    "radar_technique_created": True,
                    "technique_name": technique.name
                }
            else:
                return {"success": False, "error": "Failed to create RadarTechnique node"}
                
        except Exception as e:
            logger.error(f"Failed to ingest radar technique {technique.name}: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_connection(self, connection: Dict[str, str]) -> None:
        """Create a connection between two nodes.
        
        Args:
            connection: Dictionary with connection details
        """
        if connection["type"] == "SUPPORTED_BY":
            # Link rule to evidence
            success = self.evidence_repo.link_to_rule(
                connection["to_name"],  # evidence name
                connection["from_name"]  # rule name
            )
            if not success:
                raise RuntimeError(f"Failed to create {connection['type']} relationship")
    
    def _link_radar_technique_to_practices(self, technique: RadarTechnique) -> None:
        """Link RadarTechnique to related practices using Cypher 25.
        
        Args:
            technique: RadarTechnique to link
        """
        try:
            # Find practices that might be related to this technique
            query = """
            CYPHER 25
            MATCH (rt:RadarTechnique {name: $technique_name})
            MATCH (p:Practice)
            WHERE p.name CONTAINS $technique_keyword 
               OR p.description CONTAINS $technique_keyword
               OR $technique_keyword IN p.tools
            MERGE (rt)-[:INFLUENCES_PRACTICE]->(p)
            RETURN count(*) as links_created
            """
            
            # Extract keyword from technique name
            keyword = technique.name.lower().split()[0]  # First word as keyword
            
            params = {
                "technique_name": technique.name,
                "technique_keyword": keyword
            }
            
            result = self.connection.execute_write_query(query, params)
            
            if result:
                links_count = result[0]["links_created"]
                if links_count > 0:
                    logger.info(f"Linked RadarTechnique '{technique.name}' to {links_count} practices")
                    
        except Exception as e:
            logger.warning(f"Failed to link radar technique to practices: {e}")
    
    def get_radar_techniques_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all RadarTechnique nodes.
        
        Returns:
            List of radar technique summaries
        """
        try:
            query = """
            CYPHER 25
            MATCH (rt:RadarTechnique)
            OPTIONAL MATCH (rt)-[:INFLUENCES_PRACTICE]->(p:Practice)
            WITH rt, collect(p.name) as related_practices
            RETURN rt {
                .*,
                related_practices: related_practices
            } as technique
            ORDER BY rt.ring, rt.name
            """
            
            result = self.connection.execute_read_query(query)
            return [record["technique"] for record in result]
            
        except Exception as e:
            logger.error(f"Failed to get radar techniques summary: {e}")
            return []
    
    def update_radar_technique_ring(self, technique_name: str, new_ring: str) -> bool:
        """Update the ring (adoption level) of a radar technique.
        
        Args:
            technique_name: Name of the technique
            new_ring: New ring value (Adopt, Trial, Assess, Hold)
            
        Returns:
            True if updated successfully
        """
        try:
            query = """
            CYPHER 25
            MATCH (rt:RadarTechnique {name: $technique_name})
            SET rt.ring = $new_ring,
                rt.updated_at = datetime()
            RETURN rt.name as updated_technique
            """
            
            result = self.connection.execute_write_query(query, {
                "technique_name": technique_name,
                "new_ring": new_ring
            })
            
            if result:
                logger.info(f"Updated radar technique '{technique_name}' ring to '{new_ring}'")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to update radar technique ring: {e}")
            return False
