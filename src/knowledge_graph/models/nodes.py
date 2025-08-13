"""Pydantic models for Neo4j nodes."""

from typing import Optional
from pydantic import BaseModel, Field


class BaseNode(BaseModel):
    """Base class for all node models."""
    
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)


class Methodology(BaseNode):
    """Programming development methodology node."""
    
    origin: Optional[str] = Field(None, description="Origin or creator of the methodology")
    year_created: Optional[int] = Field(None, ge=1900, le=2030)
    category: Optional[str] = Field(None, description="Category like 'Agile', 'Traditional', etc.")


class Practice(BaseNode):
    """Practice within a methodology node."""
    
    tools: Optional[list[str]] = Field(default_factory=list, description="Tools used in this practice")
    difficulty_level: Optional[str] = Field(None, description="Beginner, Intermediate, Advanced")
    estimated_time: Optional[str] = Field(None, description="Estimated time to implement")


class Rule(BaseNode):
    """Rule or guideline node."""
    
    title: str = Field(..., min_length=1, max_length=200)
    detail: str = Field(..., min_length=1, max_length=2000)
    priority: Optional[str] = Field("medium", description="Priority level: low, medium, high, critical")
    category: Optional[str] = Field(None, description="Category of the rule")
    tags: Optional[list[str]] = Field(default_factory=list, description="Tags for categorization")


class Context(BaseNode):
    """Context or situation node."""
    
    constraints: Optional[list[str]] = Field(default_factory=list, description="Constraints in this context")
    team_size: Optional[str] = Field(None, description="Team size range")
    project_type: Optional[str] = Field(None, description="Type of project")
    industry: Optional[str] = Field(None, description="Industry domain")


class Evidence(BaseNode):
    """Evidence or reference node."""
    
    title: str = Field(..., min_length=1, max_length=200)
    url: Optional[str] = Field(None, description="URL to the evidence")
    summary: Optional[str] = Field(None, max_length=1000, description="Brief summary")
    source_type: Optional[str] = Field(None, description="Type: paper, blog, book, etc.")
    credibility_score: Optional[float] = Field(None, ge=0.0, le=10.0, description="Credibility from 0-10")


# Request models for API
class MethodologyCreate(BaseModel):
    """Request model for creating a methodology."""
    
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    origin: Optional[str] = None
    year_created: Optional[int] = Field(None, ge=1900, le=2030)
    category: Optional[str] = None


class PracticeCreate(BaseModel):
    """Request model for creating a practice."""
    
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    methodology_name: str = Field(..., description="Name of the parent methodology")
    tools: Optional[list[str]] = Field(default_factory=list)
    difficulty_level: Optional[str] = None
    estimated_time: Optional[str] = None


class RuleCreate(BaseModel):
    """Request model for creating a rule."""
    
    name: str = Field(..., min_length=1, max_length=200)
    title: str = Field(..., min_length=1, max_length=200)
    detail: str = Field(..., min_length=1, max_length=2000)
    practice_name: str = Field(..., description="Name of the parent practice")
    priority: Optional[str] = Field("medium")
    category: Optional[str] = None
    tags: Optional[list[str]] = Field(default_factory=list)


class ContextCreate(BaseModel):
    """Request model for creating a context."""
    
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    constraints: Optional[list[str]] = Field(default_factory=list)
    team_size: Optional[str] = None
    project_type: Optional[str] = None
    industry: Optional[str] = None


class EvidenceCreate(BaseModel):
    """Request model for creating evidence."""
    
    name: str = Field(..., min_length=1, max_length=200)
    title: str = Field(..., min_length=1, max_length=200)
    url: Optional[str] = None
    summary: Optional[str] = Field(None, max_length=1000)
    source_type: Optional[str] = None
    credibility_score: Optional[float] = Field(None, ge=0.0, le=10.0)
