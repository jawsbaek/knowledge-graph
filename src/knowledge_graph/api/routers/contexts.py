"""Context API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from ...database import ContextRepository, get_neo4j_connection
from ...models.nodes import Context, ContextCreate

router = APIRouter()


def get_context_repository() -> ContextRepository:
    """Get context repository dependency.
    
    Returns:
        ContextRepository instance
    """
    connection = get_neo4j_connection()
    return ContextRepository(connection)


@router.post("/contexts", response_model=Context, status_code=201)
async def create_context(
    context: ContextCreate,
    repo: ContextRepository = Depends(get_context_repository)
) -> Context:
    """Create a new context.
    
    Args:
        context: Context data
        repo: Repository dependency
        
    Returns:
        Created context
        
    Raises:
        HTTPException: If creation fails
    """
    try:
        result = repo.create(context)
        logger.info(f"Created context: {result.name}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to create context: {e}")
        raise HTTPException(status_code=500, detail="Failed to create context")


@router.get("/contexts", response_model=List[Context])
async def get_contexts(
    repo: ContextRepository = Depends(get_context_repository)
) -> List[Context]:
    """Get all contexts.
    
    Args:
        repo: Repository dependency
        
    Returns:
        List of all contexts
    """
    try:
        result = repo.get_all()
        logger.info(f"Retrieved {len(result)} contexts")
        return result
        
    except Exception as e:
        logger.error(f"Failed to get contexts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve contexts")
