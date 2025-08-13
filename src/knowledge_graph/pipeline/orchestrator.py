"""Pipeline orchestrator for Technology Radar data integration."""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from loguru import logger

from .ingestors.neo4j_ingestor import Neo4jRadarIngestor
from .processors.radar_processor import RadarDataProcessor
from .scrapers.thoughtworks_scraper import ThoughtWorksRadarScraper
from ..models.radar import RadarTechnique


class RadarPipelineOrchestrator:
    """Orchestrates the complete Technology Radar data pipeline."""
    
    def __init__(self):
        """Initialize the orchestrator with all components."""
        self.scraper = ThoughtWorksRadarScraper()
        self.processor = RadarDataProcessor()
        self.ingestor = Neo4jRadarIngestor()
    
    async def run_full_pipeline(self, technique_paths: Optional[List[str]] = None) -> Dict[str, any]:
        """Run the complete pipeline for Technology Radar data.
        
        Args:
            technique_paths: Optional list of specific technique paths to scrape
            
        Returns:
            Dictionary with pipeline execution results
        """
        start_time = datetime.now()
        results = {
            "start_time": start_time,
            "techniques_processed": 0,
            "total_entities_created": 0,
            "errors": [],
            "success": True
        }
        
        try:
            logger.info("🚀 Starting Technology Radar pipeline...")
            
            # Step 1: Get technique paths to scrape
            if not technique_paths:
                logger.info("📋 Fetching list of available techniques...")
                technique_paths = self.scraper.scrape_techniques_list()
                logger.info(f"Found {len(technique_paths)} techniques to scrape")
            
            # Step 2: Process each technique
            for i, technique_path in enumerate(technique_paths[:5], 1):  # Limit to 5 for demo
                logger.info(f"📊 Processing technique {i}/{min(5, len(technique_paths))}: {technique_path}")
                
                try:
                    # Scrape technique data
                    technique = self.scraper.scrape_technique(technique_path)
                    if not technique:
                        logger.warning(f"Failed to scrape technique: {technique_path}")
                        continue
                    
                    # Process technique data
                    processed_data = self.processor.process_radar_technique(technique)
                    
                    # Ingest into Neo4j
                    ingest_results = self.ingestor.ingest_processed_data(processed_data)
                    
                    # Also create dedicated RadarTechnique node
                    radar_result = self.ingestor.ingest_radar_technique_direct(technique)
                    
                    # Update results
                    results["techniques_processed"] += 1
                    results["total_entities_created"] += sum([
                        ingest_results["methodologies_created"],
                        ingest_results["practices_created"], 
                        ingest_results["rules_created"],
                        ingest_results["evidence_created"]
                    ])
                    
                    if ingest_results["errors"]:
                        results["errors"].extend(ingest_results["errors"])
                    
                    logger.info(f"✅ Completed technique: {technique.name}")
                    
                    # Add delay to be respectful to the website
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    error_msg = f"Error processing technique {technique_path}: {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
                    results["success"] = False
            
            # Step 3: Generate summary
            end_time = datetime.now()
            duration = end_time - start_time
            
            results.update({
                "end_time": end_time,
                "duration_seconds": duration.total_seconds(),
                "radar_techniques_summary": self.ingestor.get_radar_techniques_summary()
            })
            
            logger.info(f"🎉 Pipeline completed in {duration.total_seconds():.2f} seconds")
            logger.info(f"📈 Results: {results['techniques_processed']} techniques, "
                       f"{results['total_entities_created']} entities created")
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            results["success"] = False
            results["errors"].append(str(e))
        
        finally:
            self.scraper.close()
        
        return results
    
    async def run_single_technique(self, technique_name: str) -> Dict[str, any]:
        """Run pipeline for a single technique.
        
        Args:
            technique_name: Name of technique to process (e.g., "fuzz-testing")
            
        Returns:
            Dictionary with processing results
        """
        technique_path = f"/techniques/summary/{technique_name}"
        logger.info(f"🎯 Processing single technique: {technique_name}")
        
        try:
            # Scrape the specific technique
            technique = self.scraper.scrape_technique(technique_path)
            if not technique:
                return {
                    "success": False,
                    "error": f"Failed to scrape technique: {technique_name}"
                }
            
            # Process and ingest
            processed_data = self.processor.process_radar_technique(technique)
            ingest_results = self.ingestor.ingest_processed_data(processed_data)
            radar_result = self.ingestor.ingest_radar_technique_direct(technique)
            
            return {
                "success": True,
                "technique": technique.name,
                "entities_created": sum([
                    ingest_results["methodologies_created"],
                    ingest_results["practices_created"],
                    ingest_results["rules_created"], 
                    ingest_results["evidence_created"]
                ]),
                "radar_technique_created": radar_result.get("success", False),
                "errors": ingest_results.get("errors", [])
            }
            
        except Exception as e:
            logger.error(f"Failed to process technique {technique_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            self.scraper.close()
    
    def get_pipeline_status(self) -> Dict[str, any]:
        """Get current status of ingested radar data.
        
        Returns:
            Dictionary with pipeline status
        """
        try:
            techniques_summary = self.ingestor.get_radar_techniques_summary()
            
            # Group by ring
            by_ring = {}
            for technique in techniques_summary:
                ring = technique.get("ring", "Unknown")
                if ring not in by_ring:
                    by_ring[ring] = []
                by_ring[ring].append(technique["name"])
            
            return {
                "total_radar_techniques": len(techniques_summary),
                "by_ring": by_ring,
                "latest_techniques": [t["name"] for t in techniques_summary[-5:]],
                "summary": techniques_summary
            }
            
        except Exception as e:
            logger.error(f"Failed to get pipeline status: {e}")
            return {"error": str(e)}
    
    async def create_sample_radar_data(self) -> List[RadarTechnique]:
        """Create sample radar techniques based on current Technology Radar themes.
        
        Returns:
            List of RadarTechnique objects with sample data
        """
        from ..models.radar import RadarQuadrant, RadarRing, RadarMovement
        
        sample_techniques = [
            RadarTechnique(
                name="Supervised Agents in Coding Assistants",
                quadrant=RadarQuadrant.TECHNIQUES,
                ring=RadarRing.TRIAL,
                movement=RadarMovement.NEW,
                description="AI assistants that go beyond answering questions or generating small snippets; they navigate and modify code, update tests, execute commands and, in some cases, proactively fix linting and compilation errors. While we remain skeptical of coding agents that promise fully autonomous development of large tasks, we've seen promising results with this supervised approach, where developers still guide and oversee the agent's actions. Tools like Cursor, Cline and Windsurf are leading this trend.",
                volume=32,
                edition_date="2025-04",
                source_url="https://www.thoughtworks.com/radar",
                related_blips=["GitHub Copilot", "Cursor", "Cline"],
                methodology_connections=["DevOps", "Agile"],
                practice_connections=["Pair Programming", "Code Review"]
            ),
            RadarTechnique(
                name="LLM Observability",
                quadrant=RadarQuadrant.TECHNIQUES,
                ring=RadarRing.ASSESS,
                movement=RadarMovement.NEW,
                description="A critical piece in operationalizing AI. We've seen a surge in tools for monitoring and evaluating LLM performance, including Weights & Biases Weave, Arize Phoenix, Helicone and HumanLoop. The rapid innovation in observability tools demonstrates growing industry awareness of observability's importance.",
                volume=32,
                edition_date="2025-04",
                source_url="https://www.thoughtworks.com/radar",
                related_blips=["Weights & Biases Weave", "Arize Phoenix", "OpenTelemetry"],
                methodology_connections=["DevOps", "MLOps"],
                practice_connections=["Monitoring", "Performance Testing"]
            ),
            RadarTechnique(
                name="Corrective RAG",
                quadrant=RadarQuadrant.TECHNIQUES,
                ring=RadarRing.ASSESS,
                movement=RadarMovement.NEW,
                description="An advanced RAG technique that dynamically adjusts responses based on feedback or heuristics. Part of the evolving R in RAG (retrieval-augmented generation), this approach improves the quality and relevance of AI-generated responses by incorporating corrective mechanisms.",
                volume=32,
                edition_date="2025-04",
                source_url="https://www.thoughtworks.com/radar",
                related_blips=["Fusion-RAG", "Self-RAG", "FastGraphRAG"],
                methodology_connections=["AI/ML Development"],
                practice_connections=["Data Engineering", "Model Evaluation"]
            ),
            RadarTechnique(
                name="Data Product Thinking",
                quadrant=RadarQuadrant.TECHNIQUES,
                ring=RadarRing.TRIAL,
                movement=RadarMovement.NEW,
                description="A framework that encourages teams to apply the principles of product thinking to the analytic parts of their ecosystem. With the increasing presence and importance of unstructured data in the enterprise, ensuring data is effectively managed and packaged so it can be successfully leveraged for everything from AI applications to customer analytics is vital for businesses.",
                volume=32,
                edition_date="2025-04",
                source_url="https://www.thoughtworks.com/radar",
                related_blips=["Vector Databases", "Metabase"],
                methodology_connections=["Data Engineering", "Product Management"],
                practice_connections=["Data Governance", "Analytics"]
            ),
            RadarTechnique(
                name="Threat Modeling",
                quadrant=RadarQuadrant.TECHNIQUES,
                ring=RadarRing.ADOPT,
                movement=RadarMovement.NO_CHANGE,
                description="A structured approach to identifying and addressing potential security threats in software systems. This established practice helps teams proactively identify vulnerabilities and design appropriate security controls. Essential for building secure systems and should be integrated into the development lifecycle.",
                volume=32,
                edition_date="2025-04",
                source_url="https://www.thoughtworks.com/radar",
                related_blips=["Security by Design", "STRIDE"],
                methodology_connections=["Security Engineering", "DevSecOps"],
                practice_connections=["Security Assessment", "Architecture Review"]
            )
        ]
        
        logger.info(f"Created {len(sample_techniques)} sample radar techniques")
        return sample_techniques


# Convenience functions for direct usage
async def scrape_fuzz_testing():
    """Scrape and ingest Fuzz Testing technique."""
    orchestrator = RadarPipelineOrchestrator()
    return await orchestrator.run_single_technique("fuzz-testing")


async def run_demo_pipeline():
    """Run a demo pipeline with sample radar data."""
    orchestrator = RadarPipelineOrchestrator()
    
    # Create sample techniques manually since scraping URLs are not working
    sample_techniques = await orchestrator.create_sample_radar_data()
    
    # Process the sample techniques
    results = {
        "start_time": datetime.now(),
        "techniques_processed": 0,
        "total_entities_created": 0,
        "errors": [],
        "success": True
    }
    
    for technique in sample_techniques:
        try:
            # Process technique data
            processed_data = orchestrator.processor.process_radar_technique(technique)
            
            # Ingest into Neo4j
            ingest_results = orchestrator.ingestor.ingest_processed_data(processed_data)
            
            # Also create dedicated RadarTechnique node
            radar_result = orchestrator.ingestor.ingest_radar_technique_direct(technique)
            
            # Update results
            results["techniques_processed"] += 1
            results["total_entities_created"] += sum([
                ingest_results["methodologies_created"],
                ingest_results["practices_created"], 
                ingest_results["rules_created"],
                ingest_results["evidence_created"]
            ])
            
            if ingest_results["errors"]:
                results["errors"].extend(ingest_results["errors"])
                
            logger.info(f"✅ Completed technique: {technique.name}")
            
        except Exception as e:
            error_msg = f"Error processing technique {technique.name}: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
    
    end_time = datetime.now()
    duration = end_time - results["start_time"]
    
    results.update({
        "end_time": end_time,
        "duration_seconds": duration.total_seconds()
    })
    
    return results
