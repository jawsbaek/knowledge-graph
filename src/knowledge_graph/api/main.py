"""FastAPI main application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from ..database.connection import close_neo4j_connection, get_neo4j_connection
from ..utils.config import get_settings
from .routers import contexts, evidence, methodologies, practices, rules


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI lifespan event handler.
    
    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("Starting Knowledge Graph API")
    try:
        # Initialize Neo4j connection
        get_neo4j_connection()
        logger.info("Neo4j connection initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Neo4j connection: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Knowledge Graph API")
    close_neo4j_connection()


def create_app() -> FastAPI:
    """Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    settings = get_settings()
    
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )
    
    # Include routers
    app.include_router(methodologies.router, prefix="/api/v1", tags=["methodologies"])
    app.include_router(practices.router, prefix="/api/v1", tags=["practices"])
    app.include_router(rules.router, prefix="/api/v1", tags=["rules"])
    app.include_router(contexts.router, prefix="/api/v1", tags=["contexts"])
    app.include_router(evidence.router, prefix="/api/v1", tags=["evidence"])
    
    # Import and include radar router
    from .routers import radar
    app.include_router(radar.router, prefix="/api/v1", tags=["technology-radar"])
    
    @app.get("/")
    async def root() -> dict[str, str]:
        """Root endpoint."""
        return {"message": "Knowledge Graph API", "version": settings.api_version}
    
    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        try:
            # Test Neo4j connection
            connection = get_neo4j_connection()
            connection.execute_read_query("RETURN 1")
            return {"status": "healthy", "database": "connected"}
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
    
    return app


app = create_app()


def main() -> None:
    """Main entry point for running the API server."""
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "knowledge_graph.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
