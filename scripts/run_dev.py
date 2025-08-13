#!/usr/bin/env python3
"""Development server runner script."""

import subprocess
import sys
import time
from pathlib import Path


def run_neo4j() -> None:
    """Start Neo4j using Docker."""
    print("🚀 Starting Neo4j database...")
    cmd = [
        "docker", "run", "-d",
        "--name", "knowledge-graph-neo4j",
        "-p", "7474:7474", "-p", "7687:7687",
        "-e", "NEO4J_AUTH=neo4j/knowledge123",
        "-e", "NEO4J_PLUGINS=[\"apoc\"]",
        "-e", "NEO4J_ACCEPT_LICENSE_AGREEMENT=yes",
        "neo4j:2025.07.01"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Neo4j started successfully")
        print("📊 Neo4j Browser: http://localhost:7474")
        print("⚡ Bolt URI: bolt://localhost:7687")
        print("🔐 Credentials: neo4j/knowledge123")
        
        # Wait for Neo4j to be ready
        print("⏳ Waiting for Neo4j to be ready...")
        time.sleep(30)
        
    except subprocess.CalledProcessError as e:
        if "already in use" in str(e) or "already exists" in str(e):
            print("ℹ️  Neo4j container already exists, starting it...")
            subprocess.run(["docker", "start", "knowledge-graph-neo4j"])
        else:
            print(f"❌ Failed to start Neo4j: {e}")
            sys.exit(1)


def init_sample_data() -> None:
    """Initialize sample data."""
    print("📦 Initializing sample data...")
    script_path = Path(__file__).parent / "init_sample_data.py"
    
    try:
        subprocess.run([sys.executable, str(script_path)], check=True)
        print("✅ Sample data initialized")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to initialize sample data: {e}")


def run_api() -> None:
    """Start the FastAPI server."""
    print("🔥 Starting FastAPI server...")
    print("📡 API Server: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    
    try:
        subprocess.run([
            "uv", "run", "python", "-m", "knowledge_graph.api.main"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 API server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start API server: {e}")


def run_ui() -> None:
    """Start the Streamlit UI."""
    print("🎨 Starting Streamlit UI...")
    print("🌐 UI: http://localhost:8501")
    
    try:
        subprocess.run([
            "uv", "run", "streamlit", "run", 
            "src/knowledge_graph/ui/app.py",
            "--server.port=8501"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Streamlit UI stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Streamlit UI: {e}")


def main() -> None:
    """Main function to run development setup."""
    if len(sys.argv) < 2:
        print("Usage: python run_dev.py [neo4j|api|ui|sample-data|all]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "neo4j":
        run_neo4j()
    elif command == "api":
        run_api()
    elif command == "ui":
        run_ui()
    elif command == "sample-data":
        init_sample_data()
    elif command == "all":
        run_neo4j()
        init_sample_data()
        print("\n" + "="*50)
        print("🎉 Development environment ready!")
        print("📊 Neo4j Browser: http://localhost:7474")
        print("📡 API Server: http://localhost:8000")
        print("📖 API Docs: http://localhost:8000/docs")
        print("="*50 + "\n")
        
        print("Choose what to start:")
        print("1. API Server (python run_dev.py api)")
        print("2. Streamlit UI (python run_dev.py ui)")
        print("3. Both in separate terminals")
        
    else:
        print(f"Unknown command: {command}")
        print("Available commands: neo4j, api, ui, sample-data, all")
        sys.exit(1)


if __name__ == "__main__":
    main()
