"""Practice API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from ...database import PracticeRepository, get_neo4j_connection
from ...models.nodes import Practice, PracticeCreate

router = APIRouter()


def get_practice_repository() -> PracticeRepository:
    """Get practice repository dependency.
    
    Returns:
        PracticeRepository instance
    """
    connection = get_neo4j_connection()
    return PracticeRepository(connection)


@router.post("/practices", response_model=Practice, status_code=201)
async def create_practice(
    practice: PracticeCreate,
    repo: PracticeRepository = Depends(get_practice_repository)
) -> Practice:
    """Create a new practice.
    
    Args:
        practice: Practice data
        repo: Repository dependency
        
    Returns:
        Created practice
        
    Raises:
        HTTPException: If practice already exists or creation fails
    """
    try:
        # Check if practice already exists
        existing = repo.get_by_name(practice.name)
        if existing:
            raise HTTPException(
                status_code=409, 
                detail=f"Practice '{practice.name}' already exists"
            )
        
        result = repo.create(practice)
        logger.info(f"Created practice: {result.name}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create practice: {e}")
        raise HTTPException(status_code=500, detail="Failed to create practice")


@router.get("/practices/{name}", response_model=Practice)
async def get_practice(
    name: str,
    repo: PracticeRepository = Depends(get_practice_repository)
) -> Practice:
    """Get practice by name.
    
    Args:
        name: Practice name
        repo: Repository dependency
        
    Returns:
        Practice data
        
    Raises:
        HTTPException: If practice not found
    """
    try:
        result = repo.get_by_name(name)
        if not result:
            raise HTTPException(
                status_code=404, 
                detail=f"Practice '{name}' not found"
            )
        
        logger.info(f"Retrieved practice: {name}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get practice {name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve practice")


@router.get("/methodologies/{methodology_name}/practices", response_model=List[Practice])
async def get_practices_by_methodology(
    methodology_name: str,
    repo: PracticeRepository = Depends(get_practice_repository)
) -> List[Practice]:
    """Get practices for a specific methodology.
    
    Args:
        methodology_name: Methodology name
        repo: Repository dependency
        
    Returns:
        List of practices for the methodology
    """
    try:
        result = repo.get_by_methodology(methodology_name)
        logger.info(f"Retrieved {len(result)} practices for methodology: {methodology_name}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to get practices for methodology {methodology_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve practices")
