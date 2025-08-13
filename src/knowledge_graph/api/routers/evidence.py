"""Evidence API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from ...database import EvidenceRepository, get_neo4j_connection
from ...models.nodes import Evidence, EvidenceCreate

router = APIRouter()


def get_evidence_repository() -> EvidenceRepository:
    """Get evidence repository dependency.
    
    Returns:
        EvidenceRepository instance
    """
    connection = get_neo4j_connection()
    return EvidenceRepository(connection)


@router.post("/evidence", response_model=Evidence, status_code=201)
async def create_evidence(
    evidence: EvidenceCreate,
    repo: EvidenceRepository = Depends(get_evidence_repository)
) -> Evidence:
    """Create a new evidence.
    
    Args:
        evidence: Evidence data
        repo: Repository dependency
        
    Returns:
        Created evidence
        
    Raises:
        HTTPException: If creation fails
    """
    try:
        result = repo.create(evidence)
        logger.info(f"Created evidence: {result.name}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to create evidence: {e}")
        raise HTTPException(status_code=500, detail="Failed to create evidence")


@router.post("/evidence/{evidence_name}/link-rule/{rule_name}", status_code=204)
async def link_evidence_to_rule(
    evidence_name: str,
    rule_name: str,
    repo: EvidenceRepository = Depends(get_evidence_repository)
) -> None:
    """Link evidence to a rule.
    
    Args:
        evidence_name: Evidence name
        rule_name: Rule name
        repo: Repository dependency
        
    Raises:
        HTTPException: If linking fails
    """
    try:
        success = repo.link_to_rule(evidence_name, rule_name)
        if not success:
            raise HTTPException(
                status_code=404, 
                detail=f"Evidence '{evidence_name}' or Rule '{rule_name}' not found"
            )
        
        logger.info(f"Linked evidence '{evidence_name}' to rule '{rule_name}'")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to link evidence to rule: {e}")
        raise HTTPException(status_code=500, detail="Failed to link evidence to rule")
