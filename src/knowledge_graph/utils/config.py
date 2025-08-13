"""Configuration management using Pydantic Settings."""

from functools import lru_cache
from typing import List, Optional, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore"
    )
    
    # API Settings
    api_title: str = "Knowledge Graph API"
    api_version: str = "0.1.0"
    api_description: str = "Programming methodology knowledge graph management system"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    
    # Neo4j Settings
    neo4j_uri: str = Field(default="bolt://localhost:7687", description="Neo4j connection URI")
    neo4j_username: str = Field(default="neo4j", description="Neo4j username")
    neo4j_password: str = Field(default="password", description="Neo4j password")
    neo4j_database: str = Field(default="neo4j", description="Neo4j database name")
    
    # Streamlit Settings
    streamlit_host: str = "0.0.0.0"
    streamlit_port: int = 8501
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    
    # CORS
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:8501"])
    cors_methods: List[str] = Field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    cors_headers: List[str] = Field(default_factory=lambda: ["*"])
    
    @field_validator('cors_origins', 'cors_methods', 'cors_headers', mode='before')
    @classmethod
    def parse_comma_separated_list(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse comma-separated string into list."""
        if isinstance(v, str):
            if v.strip() == "":
                return []
            return [item.strip() for item in v.split(',') if item.strip()]
        return v or []


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings.
    
    Returns:
        Application settings instance
    """
    return Settings()
