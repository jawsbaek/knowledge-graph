"""Streamlit application for Knowledge Graph UI."""

import asyncio
import json
from typing import Any, Dict, List, Optional

import httpx
import streamlit as st
from loguru import logger

# Page configuration
st.set_page_config(
    page_title="Knowledge Graph - Methodology Management",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


class APIClient:
    """API client for communicating with the Knowledge Graph API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize API client.
        
        Args:
            base_url: Base URL of the API
        """
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=30.0)
    
    def get_methodologies(self) -> List[Dict[str, Any]]:
        """Get all methodologies."""
        try:
            response = self.client.get(f"{self.base_url}/api/v1/methodologies")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get methodologies: {e}")
            return []
    
    def create_methodology(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new methodology."""
        try:
            response = self.client.post(f"{self.base_url}/api/v1/methodologies", json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create methodology: {e}")
            return None
    
    def get_practices(self, methodology_name: str) -> List[Dict[str, Any]]:
        """Get practices for a methodology."""
        try:
            response = self.client.get(f"{self.base_url}/api/v1/methodologies/{methodology_name}/practices")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get practices: {e}")
            return []
    
    def create_practice(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new practice."""
        try:
            response = self.client.post(f"{self.base_url}/api/v1/practices", json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create practice: {e}")
            return None
    
    def get_rules(self, practice_name: str) -> List[Dict[str, Any]]:
        """Get rules for a practice."""
        try:
            response = self.client.get(f"{self.base_url}/api/v1/practices/{practice_name}/rules")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get rules: {e}")
            return []
    
    def create_rule(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new rule."""
        try:
            response = self.client.post(f"{self.base_url}/api/v1/rules", json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create rule: {e}")
            return None
    
    def get_contexts(self) -> List[Dict[str, Any]]:
        """Get all contexts."""
        try:
            response = self.client.get(f"{self.base_url}/api/v1/contexts")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get contexts: {e}")
            return []
    
    def create_context(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new context."""
        try:
            response = self.client.post(f"{self.base_url}/api/v1/contexts", json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create context: {e}")
            return None


@st.cache_resource
def get_api_client() -> APIClient:
    """Get cached API client."""
    api_url = st.secrets.get("API_BASE_URL", "http://localhost:8000")
    return APIClient(api_url)


def main() -> None:
    """Main Streamlit application."""
    st.title("🧠 Knowledge Graph - Programming Methodology Management")
    st.markdown("Manage and explore programming development methodologies, practices, and rules.")
    
    # Initialize API client
    api = get_api_client()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["🏠 Dashboard", "📋 Methodologies", "⚙️ Practices", "📜 Rules", "🌍 Contexts", "📊 Graph Visualization"]
    )
    
    # Main content based on selected page
    if page == "🏠 Dashboard":
        show_dashboard(api)
    elif page == "📋 Methodologies":
        show_methodologies(api)
    elif page == "⚙️ Practices":
        show_practices(api)
    elif page == "📜 Rules":
        show_rules(api)
    elif page == "🌍 Contexts":
        show_contexts(api)
    elif page == "📊 Graph Visualization":
        show_graph_visualization(api)


def show_dashboard(api: APIClient) -> None:
    """Show dashboard with overview statistics."""
    st.header("Dashboard")
    
    # Get statistics
    methodologies = api.get_methodologies()
    contexts = api.get_contexts()
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Methodologies", len(methodologies))
    
    with col2:
        total_practices = sum(len(api.get_practices(m["name"])) for m in methodologies)
        st.metric("Practices", total_practices)
    
    with col3:
        total_rules = 0
        for methodology in methodologies:
            practices = api.get_practices(methodology["name"])
            for practice in practices:
                total_rules += len(api.get_rules(practice["name"]))
        st.metric("Rules", total_rules)
    
    with col4:
        st.metric("Contexts", len(contexts))
    
    # Recent methodologies
    if methodologies:
        st.subheader("Recent Methodologies")
        for methodology in methodologies[:5]:
            with st.expander(f"📋 {methodology['name']}"):
                st.write(methodology.get("description", "No description available"))
                if methodology.get("origin"):
                    st.write(f"**Origin:** {methodology['origin']}")
                if methodology.get("category"):
                    st.write(f"**Category:** {methodology['category']}")


def show_methodologies(api: APIClient) -> None:
    """Show methodologies management page."""
    st.header("Methodologies")
    
    # Create new methodology
    with st.expander("➕ Create New Methodology"):
        with st.form("create_methodology"):
            name = st.text_input("Name*", placeholder="e.g., Agile")
            description = st.text_area("Description", placeholder="Brief description of the methodology")
            origin = st.text_input("Origin", placeholder="e.g., Kent Beck, Scrum Alliance")
            year_created = st.number_input("Year Created", min_value=1900, max_value=2030, value=None)
            category = st.selectbox("Category", ["", "Agile", "Traditional", "Hybrid", "DevOps", "Lean"])
            
            if st.form_submit_button("Create Methodology"):
                if name:
                    data = {
                        "name": name,
                        "description": description or None,
                        "origin": origin or None,
                        "year_created": year_created,
                        "category": category or None
                    }
                    result = api.create_methodology(data)
                    if result:
                        st.success(f"Methodology '{name}' created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create methodology")
                else:
                    st.error("Name is required")
    
    # List existing methodologies
    st.subheader("Existing Methodologies")
    methodologies = api.get_methodologies()
    
    if methodologies:
        for methodology in methodologies:
            with st.expander(f"📋 {methodology['name']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(methodology.get("description", "No description available"))
                    if methodology.get("origin"):
                        st.write(f"**Origin:** {methodology['origin']}")
                    if methodology.get("year_created"):
                        st.write(f"**Year:** {methodology['year_created']}")
                    if methodology.get("category"):
                        st.write(f"**Category:** {methodology['category']}")
                
                with col2:
                    practices = api.get_practices(methodology["name"])
                    st.metric("Practices", len(practices))
                    
                    if st.button(f"View Practices", key=f"practices_{methodology['name']}"):
                        st.session_state.selected_methodology = methodology["name"]
                        st.switch_page("pages/practices.py")
    else:
        st.info("No methodologies found. Create your first methodology above!")


def show_practices(api: APIClient) -> None:
    """Show practices management page."""
    st.header("Practices")
    
    methodologies = api.get_methodologies()
    
    if not methodologies:
        st.warning("No methodologies found. Please create a methodology first.")
        return
    
    # Create new practice
    with st.expander("➕ Create New Practice"):
        with st.form("create_practice"):
            methodology_name = st.selectbox(
                "Methodology*",
                [m["name"] for m in methodologies],
                placeholder="Select a methodology"
            )
            name = st.text_input("Name*", placeholder="e.g., Daily Scrum")
            description = st.text_area("Description", placeholder="Description of the practice")
            tools = st.text_input("Tools", placeholder="Comma-separated list of tools")
            difficulty_level = st.selectbox("Difficulty Level", ["", "Beginner", "Intermediate", "Advanced"])
            estimated_time = st.text_input("Estimated Time", placeholder="e.g., 15 minutes daily")
            
            if st.form_submit_button("Create Practice"):
                if name and methodology_name:
                    data = {
                        "name": name,
                        "description": description or None,
                        "methodology_name": methodology_name,
                        "tools": [t.strip() for t in tools.split(",")] if tools else [],
                        "difficulty_level": difficulty_level or None,
                        "estimated_time": estimated_time or None
                    }
                    result = api.create_practice(data)
                    if result:
                        st.success(f"Practice '{name}' created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create practice")
                else:
                    st.error("Name and methodology are required")
    
    # List practices by methodology
    st.subheader("Practices by Methodology")
    
    for methodology in methodologies:
        practices = api.get_practices(methodology["name"])
        
        if practices:
            st.write(f"### {methodology['name']}")
            
            for practice in practices:
                with st.expander(f"⚙️ {practice['name']}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(practice.get("description", "No description available"))
                        if practice.get("tools"):
                            st.write(f"**Tools:** {', '.join(practice['tools'])}")
                        if practice.get("estimated_time"):
                            st.write(f"**Estimated Time:** {practice['estimated_time']}")
                    
                    with col2:
                        if practice.get("difficulty_level"):
                            st.write(f"**Difficulty:** {practice['difficulty_level']}")
                        
                        rules = api.get_rules(practice["name"])
                        st.metric("Rules", len(rules))


def show_rules(api: APIClient) -> None:
    """Show rules management page."""
    st.header("Rules")
    
    methodologies = api.get_methodologies()
    
    if not methodologies:
        st.warning("No methodologies found. Please create a methodology first.")
        return
    
    # Get all practices
    all_practices = []
    for methodology in methodologies:
        practices = api.get_practices(methodology["name"])
        all_practices.extend(practices)
    
    if not all_practices:
        st.warning("No practices found. Please create practices first.")
        return
    
    # Create new rule
    with st.expander("➕ Create New Rule"):
        with st.form("create_rule"):
            practice_name = st.selectbox(
                "Practice*",
                [p["name"] for p in all_practices],
                placeholder="Select a practice"
            )
            name = st.text_input("Name*", placeholder="e.g., daily-standup-rule")
            title = st.text_input("Title*", placeholder="e.g., Daily Stand-up Meeting")
            detail = st.text_area("Detail*", placeholder="Detailed description of the rule")
            priority = st.selectbox("Priority", ["low", "medium", "high", "critical"])
            category = st.text_input("Category", placeholder="e.g., meetings, communication")
            tags = st.text_input("Tags", placeholder="Comma-separated tags")
            
            if st.form_submit_button("Create Rule"):
                if name and title and detail and practice_name:
                    data = {
                        "name": name,
                        "title": title,
                        "detail": detail,
                        "practice_name": practice_name,
                        "priority": priority,
                        "category": category or None,
                        "tags": [t.strip() for t in tags.split(",")] if tags else []
                    }
                    result = api.create_rule(data)
                    if result:
                        st.success(f"Rule '{title}' created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create rule")
                else:
                    st.error("Name, title, detail, and practice are required")
    
    # List rules by practice
    st.subheader("Rules by Practice")
    
    for practice in all_practices:
        rules = api.get_rules(practice["name"])
        
        if rules:
            st.write(f"### {practice['name']}")
            
            for rule in rules:
                priority_color = {
                    "low": "🟢",
                    "medium": "🟡", 
                    "high": "🟠",
                    "critical": "🔴"
                }.get(rule.get("priority", "medium"), "🟡")
                
                with st.expander(f"{priority_color} {rule['title']}"):
                    st.write(rule["detail"])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if rule.get("category"):
                            st.write(f"**Category:** {rule['category']}")
                        st.write(f"**Priority:** {rule.get('priority', 'medium')}")
                    
                    with col2:
                        if rule.get("tags"):
                            st.write(f"**Tags:** {', '.join(rule['tags'])}")


def show_contexts(api: APIClient) -> None:
    """Show contexts management page."""
    st.header("Contexts")
    
    # Create new context
    with st.expander("➕ Create New Context"):
        with st.form("create_context"):
            name = st.text_input("Name*", placeholder="e.g., Remote Team")
            description = st.text_area("Description", placeholder="Description of the context")
            constraints = st.text_input("Constraints", placeholder="Comma-separated constraints")
            team_size = st.selectbox("Team Size", ["", "1-3", "4-7", "8-15", "16+"])
            project_type = st.selectbox("Project Type", ["", "Web App", "Mobile App", "API", "Desktop", "Embedded"])
            industry = st.text_input("Industry", placeholder="e.g., Finance, Healthcare, E-commerce")
            
            if st.form_submit_button("Create Context"):
                if name:
                    data = {
                        "name": name,
                        "description": description or None,
                        "constraints": [c.strip() for c in constraints.split(",")] if constraints else [],
                        "team_size": team_size or None,
                        "project_type": project_type or None,
                        "industry": industry or None
                    }
                    result = api.create_context(data)
                    if result:
                        st.success(f"Context '{name}' created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create context")
                else:
                    st.error("Name is required")
    
    # List existing contexts
    st.subheader("Existing Contexts")
    contexts = api.get_contexts()
    
    if contexts:
        for context in contexts:
            with st.expander(f"🌍 {context['name']}"):
                st.write(context.get("description", "No description available"))
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if context.get("team_size"):
                        st.write(f"**Team Size:** {context['team_size']}")
                    if context.get("project_type"):
                        st.write(f"**Project Type:** {context['project_type']}")
                
                with col2:
                    if context.get("industry"):
                        st.write(f"**Industry:** {context['industry']}")
                    if context.get("constraints"):
                        st.write(f"**Constraints:** {', '.join(context['constraints'])}")
    else:
        st.info("No contexts found. Create your first context above!")


def show_graph_visualization(api: APIClient) -> None:
    """Show graph visualization page."""
    st.header("Graph Visualization")
    st.info("Graph visualization will be implemented in the next version using libraries like Pyvis or NetworkX.")
    
    # Placeholder for future graph visualization
    st.subheader("Network Overview")
    
    methodologies = api.get_methodologies()
    if methodologies:
        st.write("### Methodology-Practice-Rule Relationships")
        
        for methodology in methodologies:
            st.write(f"**{methodology['name']}**")
            practices = api.get_practices(methodology["name"])
            
            for practice in practices:
                st.write(f"  └── {practice['name']}")
                rules = api.get_rules(practice["name"])
                
                for rule in rules:
                    priority_icon = {
                        "low": "🟢",
                        "medium": "🟡",
                        "high": "🟠", 
                        "critical": "🔴"
                    }.get(rule.get("priority", "medium"), "🟡")
                    
                    st.write(f"      └── {priority_icon} {rule['title']}")


if __name__ == "__main__":
    main()
