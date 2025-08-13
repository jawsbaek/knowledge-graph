#!/usr/bin/env python3
"""Script to run the Technology Radar data pipeline."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from knowledge_graph.pipeline.orchestrator import RadarPipelineOrchestrator, scrape_fuzz_testing, run_demo_pipeline


async def main():
    """Main function to run radar pipeline."""
    if len(sys.argv) < 2:
        print("Usage: python run_radar_pipeline.py [demo|fuzz-testing|technique_name]")
        print("Examples:")
        print("  python run_radar_pipeline.py demo")
        print("  python run_radar_pipeline.py fuzz-testing")
        print("  python run_radar_pipeline.py threat-modeling")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == "demo":
            print("🚀 Running demo Technology Radar pipeline...")
            result = await run_demo_pipeline()
        elif command == "fuzz-testing":
            print("🎯 Scraping Fuzz Testing technique...")
            result = await scrape_fuzz_testing()
        else:
            print(f"🎯 Scraping technique: {command}")
            orchestrator = RadarPipelineOrchestrator()
            result = await orchestrator.run_single_technique(command)
        
        # Print results
        print("\n" + "="*60)
        print("📊 PIPELINE RESULTS")
        print("="*60)
        
        if result.get("success", True):
            print("✅ Status: SUCCESS")
            if "techniques_processed" in result:
                print(f"📈 Techniques processed: {result['techniques_processed']}")
                print(f"🏗️  Total entities created: {result['total_entities_created']}")
                print(f"⏱️  Duration: {result.get('duration_seconds', 0):.2f} seconds")
            else:
                print(f"🎯 Technique: {result.get('technique', 'Unknown')}")
                print(f"🏗️  Entities created: {result.get('entities_created', 0)}")
                print(f"📊 Radar technique created: {result.get('radar_technique_created', False)}")
        else:
            print("❌ Status: FAILED")
            print(f"💥 Error: {result.get('error', 'Unknown error')}")
        
        if result.get("errors"):
            print(f"⚠️  Errors encountered: {len(result['errors'])}")
            for error in result["errors"][:3]:  # Show first 3 errors
                print(f"   - {error}")
        
        print("="*60)
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
