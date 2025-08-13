"""Technology Radar API endpoints."""

from typing import Any, Dict, List

from fastapi import APIRouter, BackgroundTasks, HTTPException
from loguru import logger

from ...models.radar import RadarItemCreate, RadarItemUpdate
from ...pipeline.orchestrator import RadarPipelineOrchestrator

router = APIRouter()


@router.post("/radar/ingest/technique/{technique_name}")
async def ingest_technique(
    technique_name: str,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Ingest a specific technique from Technology Radar.
    
    Args:
        technique_name: Name of technique (e.g., "fuzz-testing")
        background_tasks: FastAPI background tasks
        
    Returns:
        Ingestion result summary
    """
    try:
        logger.info(f"Starting ingestion for technique: {technique_name}")
        
        # Run the pipeline for this specific technique
        orchestrator = RadarPipelineOrchestrator()
        result = await orchestrator.run_single_technique(technique_name)
        
        if result["success"]:
            logger.info(f"Successfully ingested technique: {technique_name}")
            return {
                "message": f"Successfully ingested technique: {technique_name}",
                "technique": result["technique"],
                "entities_created": result["entities_created"],
                "radar_technique_created": result["radar_technique_created"]
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to ingest technique: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        logger.error(f"Failed to ingest technique {technique_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/radar/ingest/demo")
async def run_demo_ingestion(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Run demo ingestion with a few high-value techniques.
    
    Returns:
        Demo ingestion results
    """
    try:
        logger.info("Starting demo radar ingestion...")
        
        orchestrator = RadarPipelineOrchestrator()
        
        # Demo techniques focusing on quality and security
        demo_techniques = [
            "/techniques/summary/fuzz-testing",
            "/techniques/summary/threat-modeling",
            "/techniques/summary/software-bill-of-materials"
        ]
        
        result = await orchestrator.run_full_pipeline(demo_techniques)
        
        return {
            "message": "Demo ingestion completed",
            "techniques_processed": result["techniques_processed"],
            "total_entities_created": result["total_entities_created"],
            "duration_seconds": result.get("duration_seconds", 0),
            "success": result["success"],
            "errors": result.get("errors", [])
        }
        
    except Exception as e:
        logger.error(f"Demo ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/radar/status")
async def get_radar_status() -> Dict[str, Any]:
    """Get current status of Technology Radar data in the knowledge graph.
    
    Returns:
        Status summary of radar data
    """
    try:
        orchestrator = RadarPipelineOrchestrator()
        status = orchestrator.get_pipeline_status()
        
        return {
            "status": "success",
            "radar_data": status
        }
        
    except Exception as e:
        logger.error(f"Failed to get radar status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/radar/techniques")
async def get_radar_techniques() -> List[Dict[str, Any]]:
    """Get all Technology Radar techniques stored in the knowledge graph.
    
    Returns:
        List of radar techniques with their details
    """
    try:
        orchestrator = RadarPipelineOrchestrator()
        techniques = orchestrator.ingestor.get_radar_techniques_summary()
        
        return techniques
        
    except Exception as e:
        logger.error(f"Failed to get radar techniques: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/radar/techniques/{technique_name}/ring")
async def update_technique_ring(
    technique_name: str,
    new_ring: str
) -> Dict[str, Any]:
    """Update the adoption ring of a Technology Radar technique.
    
    Args:
        technique_name: Name of the technique
        new_ring: New ring value (Adopt, Trial, Assess, Hold)
        
    Returns:
        Update result
    """
    try:
        # Validate ring value
        valid_rings = ["Adopt", "Trial", "Assess", "Hold"]
        if new_ring not in valid_rings:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid ring value. Must be one of: {valid_rings}"
            )
        
        orchestrator = RadarPipelineOrchestrator()
        success = orchestrator.ingestor.update_radar_technique_ring(technique_name, new_ring)
        
        if success:
            return {
                "message": f"Updated technique '{technique_name}' ring to '{new_ring}'",
                "technique": technique_name,
                "new_ring": new_ring
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Technique '{technique_name}' not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update technique ring: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/radar/techniques/{technique_name}/connections")
async def get_technique_connections(technique_name: str) -> Dict[str, Any]:
    """Get connections between a radar technique and methodology practices.
    
    Args:
        technique_name: Name of the technique
        
    Returns:
        Dictionary with technique connections
    """
    try:
        from ...database import get_neo4j_connection
        
        connection = get_neo4j_connection()
        
        query = """
        CYPHER 25
        MATCH (rt:RadarTechnique {name: $technique_name})
        OPTIONAL MATCH (rt)-[:INFLUENCES_PRACTICE]->(p:Practice)
        OPTIONAL MATCH (p)<-[:HAS_PRACTICE]-(m:Methodology)
        OPTIONAL MATCH (p)-[:HAS_RULE]->(r:Rule)
        RETURN rt {
            .*,
            connected_practices: collect(DISTINCT p.name),
            connected_methodologies: collect(DISTINCT m.name),
            related_rules: collect(DISTINCT r.title)
        } as technique_with_connections
        """
        
        result = connection.execute_read_query(query, {"technique_name": technique_name})
        
        if result:
            return result[0]["technique_with_connections"]
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Technique '{technique_name}' not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get technique connections: {e}")
        raise HTTPException(status_code=500, detail=str(e))
