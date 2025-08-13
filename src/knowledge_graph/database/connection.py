"""Neo4j database connection management."""

from typing import Any, Dict, List, Optional

from neo4j import GraphDatabase, Driver, Session
from loguru import logger

from ..utils.config import get_settings


class Neo4jConnection:
    """Neo4j database connection manager."""
    
    def __init__(self, uri: str, username: str, password: str, database: str = "neo4j"):
        """Initialize Neo4j connection.
        
        Args:
            uri: Neo4j connection URI
            username: Database username
            password: Database password
            database: Database name
        """
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self._driver: Optional[Driver] = None
    
    def connect(self) -> None:
        """Establish connection to Neo4j database."""
        try:
            self._driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.username, self.password)
            )
            # Test connection
            with self._driver.session(database=self.database) as session:
                session.run("RETURN 1")
            logger.info(f"Connected to Neo4j database: {self.database}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    def close(self) -> None:
        """Close the database connection."""
        if self._driver:
            self._driver.close()
            self._driver = None
            logger.info("Neo4j connection closed")
    
    def get_session(self) -> Session:
        """Get a new database session.
        
        Returns:
            Neo4j session object
            
        Raises:
            RuntimeError: If not connected to database
        """
        if not self._driver:
            raise RuntimeError("Not connected to Neo4j database")
        return self._driver.session(database=self.database)
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            
        Returns:
            List of result records as dictionaries
        """
        with self.get_session() as session:
            result = session.run(query, parameters or {})
            return [dict(record) for record in result]
    
    def execute_write_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a write Cypher query and return results.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            
        Returns:
            List of result records as dictionaries
        """
        with self.get_session() as session:
            result = session.execute_write(lambda tx: tx.run(query, parameters or {}))
            return [dict(record) for record in result]
    
    def execute_read_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a read Cypher query and return results.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            
        Returns:
            List of result records as dictionaries
        """
        with self.get_session() as session:
            result = session.execute_read(lambda tx: tx.run(query, parameters or {}))
            return [dict(record) for record in result]


# Global connection instance
_neo4j_connection: Optional[Neo4jConnection] = None


def get_neo4j_connection() -> Neo4jConnection:
    """Get the global Neo4j connection instance.
    
    Returns:
        Neo4j connection instance
    """
    global _neo4j_connection
    
    if _neo4j_connection is None:
        settings = get_settings()
        _neo4j_connection = Neo4jConnection(
            uri=settings.neo4j_uri,
            username=settings.neo4j_username,
            password=settings.neo4j_password,
            database=settings.neo4j_database
        )
        _neo4j_connection.connect()
    
    return _neo4j_connection


def close_neo4j_connection() -> None:
    """Close the global Neo4j connection."""
    global _neo4j_connection
    
    if _neo4j_connection:
        _neo4j_connection.close()
        _neo4j_connection = None
