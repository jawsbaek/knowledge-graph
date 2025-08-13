"""Rule API endpoints with Cypher 25 support."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from ...database import RuleRepository, get_neo4j_connection
from ...models.nodes import Rule, RuleCreate

router = APIRouter()


def get_rule_repository() -> RuleRepository:
    """Get rule repository dependency.
    
    Returns:
        RuleRepository instance
    """
    connection = get_neo4j_connection()
    return RuleRepository(connection)


@router.post("/rules", response_model=Rule, status_code=201)
async def create_rule(
    rule: RuleCreate,
    repo: RuleRepository = Depends(get_rule_repository)
) -> Rule:
    """Create a new rule.
    
    Args:
        rule: Rule data
        repo: Repository dependency
        
    Returns:
        Created rule
        
    Raises:
        HTTPException: If creation fails
    """
    try:
        result = repo.create(rule)
        logger.info(f"Created rule: {result.name}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to create rule: {e}")
        raise HTTPException(status_code=500, detail="Failed to create rule")


@router.get("/practices/{practice_name}/rules", response_model=List[Rule])
async def get_rules_by_practice(
    practice_name: str,
    repo: RuleRepository = Depends(get_rule_repository)
) -> List[Rule]:
    """Get rules for a specific practice.
    
    Args:
        practice_name: Practice name
        repo: Repository dependency
        
    Returns:
        List of rules for the practice
    """
    try:
        result = repo.get_by_practice(practice_name)
        logger.info(f"Retrieved {len(result)} rules for practice: {practice_name}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to get rules for practice {practice_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve rules")


@router.get("/contexts/{context_name}/rules", response_model=List[Rule])
async def get_rules_by_context(
    context_name: str,
    repo: RuleRepository = Depends(get_rule_repository)
) -> List[Rule]:
    """Get rules applicable in a specific context.
    
    Args:
        context_name: Context name
        repo: Repository dependency
        
    Returns:
        List of applicable rules
    """
    try:
        result = repo.get_by_context(context_name)
        logger.info(f"Retrieved {len(result)} rules for context: {context_name}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to get rules for context {context_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve rules")


@router.get("/practices/{practice_name}/rules-with-evidence", response_model=List[Dict[str, Any]])
async def get_rules_with_evidence(
    practice_name: str,
    repo: RuleRepository = Depends(get_rule_repository)
) -> List[Dict[str, Any]]:
    """Get rules with their supporting evidence using Cypher 25 COLLECT subqueries.
    
    Args:
        practice_name: Practice name
        repo: Repository dependency
        
    Returns:
        List of rules with evidence
    """
    try:
        result = repo.get_rules_with_evidence(practice_name)
        logger.info(f"Retrieved {len(result)} rules with evidence for practice: {practice_name}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to get rules with evidence for practice {practice_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve rules with evidence")


@router.post("/rules/find-applicable", response_model=List[Rule])
async def find_applicable_rules(
    constraints: List[str],
    team_size: str = None,
    repo: RuleRepository = Depends(get_rule_repository)
) -> List[Rule]:
    """Find applicable rules based on context constraints using Cypher 25 EXISTS.
    
    Args:
        constraints: List of context constraints
        team_size: Optional team size filter
        repo: Repository dependency
        
    Returns:
        List of applicable rules
    """
    try:
        result = repo.find_applicable_rules(constraints, team_size)
        logger.info(f"Found {len(result)} applicable rules for constraints: {constraints}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to find applicable rules: {e}")
        raise HTTPException(status_code=500, detail="Failed to find applicable rules")
