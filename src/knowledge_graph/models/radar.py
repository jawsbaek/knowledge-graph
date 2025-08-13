"""Pydantic models for ThoughtWorks Technology Radar data."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class RadarQuadrant(str, Enum):
    """Technology Radar quadrants."""
    
    TECHNIQUES = "Techniques"
    TOOLS = "Tools"
    PLATFORMS = "Platforms"
    LANGUAGES_FRAMEWORKS = "Languages & Frameworks"


class RadarRing(str, Enum):
    """Technology Radar rings (adoption levels)."""
    
    ADOPT = "Adopt"
    TRIAL = "Trial"
    ASSESS = "Assess"
    HOLD = "Hold"


class RadarMovement(str, Enum):
    """Technology Radar movement indicators."""
    
    NEW = "New"
    MOVED_IN = "Moved in"
    MOVED_OUT = "Moved out"
    NO_CHANGE = "No change"


class RadarItem(BaseModel):
    """Base model for Technology Radar items."""
    
    name: str = Field(..., min_length=1, max_length=200)
    quadrant: RadarQuadrant
    ring: RadarRing
    movement: RadarMovement = RadarMovement.NO_CHANGE
    description: str = Field(..., min_length=10)
    volume: int = Field(..., ge=1, description="Radar volume/edition number")
    edition_date: str = Field(..., description="Edition date in YYYY-MM format")
    source_url: Optional[HttpUrl] = None
    related_blips: List[str] = Field(default_factory=list, description="Names of related radar items")
    

class RadarTechnique(RadarItem):
    """Technology Radar technique item."""
    
    quadrant: RadarQuadrant = RadarQuadrant.TECHNIQUES
    methodology_connections: List[str] = Field(default_factory=list, description="Connected methodologies")
    practice_connections: List[str] = Field(default_factory=list, description="Connected practices")
    

class RadarTool(RadarItem):
    """Technology Radar tool item."""
    
    quadrant: RadarQuadrant = RadarQuadrant.TOOLS
    tool_category: Optional[str] = None
    supported_platforms: List[str] = Field(default_factory=list)


class RadarPlatform(RadarItem):
    """Technology Radar platform item."""
    
    quadrant: RadarQuadrant = RadarQuadrant.PLATFORMS
    deployment_model: Optional[str] = None
    vendor: Optional[str] = None


class RadarLanguageFramework(RadarItem):
    """Technology Radar language/framework item."""
    
    quadrant: RadarQuadrant = RadarQuadrant.LANGUAGES_FRAMEWORKS
    language_type: Optional[str] = None
    framework_type: Optional[str] = None


class RadarEdition(BaseModel):
    """Technology Radar edition metadata."""
    
    volume: int = Field(..., ge=1)
    edition_date: str = Field(..., description="Edition date in YYYY-MM format")
    title: str = Field(..., description="Edition title")
    published_date: datetime
    total_items: int = Field(..., ge=0)
    new_items: int = Field(..., ge=0)
    moved_items: int = Field(..., ge=0)
    

# Request models for API
class RadarItemCreate(BaseModel):
    """Request model for creating radar items."""
    
    name: str = Field(..., min_length=1, max_length=200)
    quadrant: RadarQuadrant
    ring: RadarRing
    movement: RadarMovement = RadarMovement.NO_CHANGE
    description: str = Field(..., min_length=10)
    volume: int = Field(..., ge=1)
    edition_date: str
    source_url: Optional[str] = None
    related_blips: List[str] = Field(default_factory=list)
    

class RadarItemUpdate(BaseModel):
    """Request model for updating radar items."""
    
    ring: Optional[RadarRing] = None
    movement: Optional[RadarMovement] = None
    description: Optional[str] = None
    related_blips: Optional[List[str]] = None
