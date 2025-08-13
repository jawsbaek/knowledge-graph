"""Methodology API endpoints with Cypher 25 support."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from ...database import MethodologyRepository, get_neo4j_connection
from ...models.nodes import Methodology, MethodologyCreate

router = APIRouter()


def get_methodology_repository() -> MethodologyRepository:
    """Get methodology repository dependency.
    
    Returns:
        MethodologyRepository instance
    """
    connection = get_neo4j_connection()
    return MethodologyRepository(connection)


@router.post("/methodologies", response_model=Methodology, status_code=201)
async def create_methodology(
    methodology: MethodologyCreate,
    repo: MethodologyRepository = Depends(get_methodology_repository)
) -> Methodology:
    """Create a new methodology.
    
    Args:
        methodology: Methodology data
        repo: Repository dependency
        
    Returns:
        Created methodology
        
    Raises:
        HTTPException: If methodology already exists or creation fails
    """
    try:
        # Check if methodology already exists
        existing = repo.get_by_name(methodology.name)
        if existing:
            raise HTTPException(
                status_code=409, 
                detail=f"Methodology '{methodology.name}' already exists"
            )
        
        result = repo.create(methodology)
        logger.info(f"Created methodology: {result.name}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create methodology: {e}")
        raise HTTPException(status_code=500, detail="Failed to create methodology")


@router.get("/methodologies", response_model=List[Methodology])
async def get_methodologies(
    repo: MethodologyRepository = Depends(get_methodology_repository)
) -> List[Methodology]:
    """Get all methodologies.
    
    Args:
        repo: Repository dependency
        
    Returns:
        List of all methodologies
    """
    try:
        result = repo.get_all()
        logger.info(f"Retrieved {len(result)} methodologies")
        return result
        
    except Exception as e:
        logger.error(f"Failed to get methodologies: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve methodologies")


@router.get("/methodologies/{name}", response_model=Methodology)
async def get_methodology(
    name: str,
    repo: MethodologyRepository = Depends(get_methodology_repository)
) -> Methodology:
    """Get methodology by name.
    
    Args:
        name: Methodology name
        repo: Repository dependency
        
    Returns:
        Methodology data
        
    Raises:
        HTTPException: If methodology not found
    """
    try:
        result = repo.get_by_name(name)
        if not result:
            raise HTTPException(
                status_code=404, 
                detail=f"Methodology '{name}' not found"
            )
        
        logger.info(f"Retrieved methodology: {name}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get methodology {name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve methodology")


@router.delete("/methodologies/{name}", status_code=204)
async def delete_methodology(
    name: str,
    repo: MethodologyRepository = Depends(get_methodology_repository)
) -> None:
    """Delete methodology by name.
    
    Args:
        name: Methodology name
        repo: Repository dependency
        
    Raises:
        HTTPException: If methodology not found
    """
    try:
        deleted = repo.delete(name)
        if not deleted:
            raise HTTPException(
                status_code=404, 
                detail=f"Methodology '{name}' not found"
            )
        
        logger.info(f"Deleted methodology: {name}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete methodology {name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete methodology")


@router.get("/methodologies/{name}/related", response_model=List[Methodology])
async def get_related_methodologies(
    name: str,
    limit: int = 5,
    repo: MethodologyRepository = Depends(get_methodology_repository)
) -> List[Methodology]:
    """Get methodologies related to the specified one using Cypher 25 features.
    
    Args:
        name: Methodology name
        limit: Maximum number of related methodologies
        repo: Repository dependency
        
    Returns:
        List of related methodologies
    """
    try:
        result = repo.find_related_methodologies(name, limit)
        logger.info(f"Found {len(result)} related methodologies for: {name}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to get related methodologies for {name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve related methodologies")


@router.get("/methodologies/{name}/full", response_model=Dict[str, Any])
async def get_methodology_with_details(
    name: str,
    repo: MethodologyRepository = Depends(get_methodology_repository)
) -> Dict[str, Any]:
    """Get methodology with all practices and rules using Cypher 25 COLLECT subqueries.
    
    Args:
        name: Methodology name
        repo: Repository dependency
        
    Returns:
        Complete methodology data with practices and rules
    """
    try:
        result = repo.get_with_practices_and_rules(name)
        if not result:
            raise HTTPException(
                status_code=404, 
                detail=f"Methodology '{name}' not found"
            )
        
        logger.info(f"Retrieved full details for methodology: {name}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get methodology details for {name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve methodology details")
