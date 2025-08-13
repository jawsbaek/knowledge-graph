"""Initialize sample data for the Knowledge Graph."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from knowledge_graph.database import (
    ContextRepository,
    EvidenceRepository,
    MethodologyRepository,
    PracticeRepository,
    RuleRepository,
    get_neo4j_connection,
)
from knowledge_graph.models.nodes import (
    ContextCreate,
    EvidenceCreate,
    MethodologyCreate,
    PracticeCreate,
    RuleCreate,
)


def create_sample_data() -> None:
    """Create sample data for the knowledge graph."""
    # Get database connection
    connection = get_neo4j_connection()
    
    # Initialize repositories
    methodology_repo = MethodologyRepository(connection)
    practice_repo = PracticeRepository(connection)
    rule_repo = RuleRepository(connection)
    context_repo = ContextRepository(connection)
    evidence_repo = EvidenceRepository(connection)
    
    print("🚀 Creating sample data...")
    
    # Create Methodologies
    methodologies = [
        MethodologyCreate(
            name="Agile",
            description="Iterative development methodology focusing on collaboration, customer feedback, and rapid delivery",
            origin="Agile Manifesto Authors",
            year_created=2001,
            category="Agile"
        ),
        MethodologyCreate(
            name="Scrum",
            description="Framework for developing and sustaining complex products in a complex environment",
            origin="Ken Schwaber and Jeff Sutherland",
            year_created=1995,
            category="Agile"
        ),
        MethodologyCreate(
            name="Waterfall",
            description="Sequential development process where progress flows downwards through distinct phases",
            origin="Winston W. Royce",
            year_created=1970,
            category="Traditional"
        ),
        MethodologyCreate(
            name="DevOps",
            description="Set of practices that combines software development and IT operations",
            origin="Patrick Debois",
            year_created=2009,
            category="DevOps"
        ),
        MethodologyCreate(
            name="Kanban",
            description="Visual workflow management method for defining, managing and improving services",
            origin="Toyota Production System",
            year_created=1940,
            category="Lean"
        )
    ]
    
    for methodology in methodologies:
        try:
            result = methodology_repo.create(methodology)
            print(f"✅ Created methodology: {result.name}")
        except Exception as e:
            print(f"❌ Failed to create methodology {methodology.name}: {e}")
    
    # Create Practices
    practices = [
        # Agile practices
        PracticeCreate(
            name="User Stories",
            description="Short, simple descriptions of features told from the perspective of the end user",
            methodology_name="Agile",
            tools=["Jira", "Azure DevOps", "Trello"],
            difficulty_level="Beginner",
            estimated_time="2-4 hours per story"
        ),
        PracticeCreate(
            name="Sprint Planning",
            description="Event in Scrum where the team plans work to be performed during the sprint",
            methodology_name="Agile",
            tools=["Jira", "Azure DevOps", "Miro"],
            difficulty_level="Intermediate",
            estimated_time="2-4 hours per sprint"
        ),
        
        # Scrum practices
        PracticeCreate(
            name="Daily Scrum",
            description="Daily time-boxed event for the development team to synchronize activities",
            methodology_name="Scrum",
            tools=["Teams", "Slack", "Zoom"],
            difficulty_level="Beginner",
            estimated_time="15 minutes daily"
        ),
        PracticeCreate(
            name="Sprint Review",
            description="Event where the Scrum Team and stakeholders inspect the increment",
            methodology_name="Scrum",
            tools=["Teams", "PowerPoint", "Demo environment"],
            difficulty_level="Intermediate",
            estimated_time="1-2 hours per sprint"
        ),
        PracticeCreate(
            name="Sprint Retrospective",
            description="Event where the Scrum Team inspects itself and creates improvement plans",
            methodology_name="Scrum",
            tools=["Miro", "Retrium", "FunRetro"],
            difficulty_level="Intermediate",
            estimated_time="1-2 hours per sprint"
        ),
        
        # DevOps practices
        PracticeCreate(
            name="Continuous Integration",
            description="Practice of merging developer working copies to a shared mainline frequently",
            methodology_name="DevOps",
            tools=["Jenkins", "GitHub Actions", "Azure DevOps"],
            difficulty_level="Advanced",
            estimated_time="Initial setup: 1-2 weeks"
        ),
        PracticeCreate(
            name="Infrastructure as Code",
            description="Managing and provisioning infrastructure through machine-readable definition files",
            methodology_name="DevOps",
            tools=["Terraform", "Ansible", "CloudFormation"],
            difficulty_level="Advanced",
            estimated_time="Setup: 2-4 weeks"
        ),
        
        # Kanban practices
        PracticeCreate(
            name="Visualize Workflow",
            description="Make work visible through boards and cards representing work items",
            methodology_name="Kanban",
            tools=["Kanban boards", "Jira", "Trello"],
            difficulty_level="Beginner",
            estimated_time="1-2 days setup"
        ),
        PracticeCreate(
            name="Limit Work in Progress",
            description="Constrain how much work can be in each stage of the workflow",
            methodology_name="Kanban",
            tools=["Physical boards", "Digital tools"],
            difficulty_level="Intermediate",
            estimated_time="Ongoing adjustment"
        )
    ]
    
    for practice in practices:
        try:
            result = practice_repo.create(practice)
            print(f"✅ Created practice: {result.name}")
        except Exception as e:
            print(f"❌ Failed to create practice {practice.name}: {e}")
    
    # Create Rules
    rules = [
        # Daily Scrum rules
        RuleCreate(
            name="daily-scrum-timebox",
            title="Daily Scrum Time-box",
            detail="The Daily Scrum is time-boxed to 15 minutes regardless of team size",
            practice_name="Daily Scrum",
            priority="high",
            category="timeboxing",
            tags=["scrum", "meeting", "timebox"]
        ),
        RuleCreate(
            name="daily-scrum-three-questions",
            title="Three Questions Format",
            detail="Each team member answers: What did I do yesterday? What will I do today? What impediments are in my way?",
            practice_name="Daily Scrum",
            priority="high",
            category="format",
            tags=["scrum", "questions", "format"]
        ),
        
        # Sprint Planning rules
        RuleCreate(
            name="sprint-planning-capacity",
            title="Team Capacity Planning",
            detail="Consider team member availability, holidays, and other commitments when planning sprint capacity",
            practice_name="Sprint Planning",
            priority="high",
            category="planning",
            tags=["capacity", "planning", "team"]
        ),
        
        # User Stories rules
        RuleCreate(
            name="user-story-invest",
            title="INVEST Criteria",
            detail="User stories should be Independent, Negotiable, Valuable, Estimable, Small, and Testable",
            practice_name="User Stories",
            priority="high",
            category="quality",
            tags=["invest", "criteria", "quality"]
        ),
        
        # CI rules
        RuleCreate(
            name="ci-commit-frequency",
            title="Frequent Commits",
            detail="Developers should commit code to the main branch at least once per day",
            practice_name="Continuous Integration",
            priority="medium",
            category="frequency",
            tags=["commits", "integration", "frequency"]
        ),
        RuleCreate(
            name="ci-automated-tests",
            title="Automated Test Suite",
            detail="Every commit should trigger automated tests to ensure code quality",
            practice_name="Continuous Integration",
            priority="critical",
            category="testing",
            tags=["automation", "testing", "quality"]
        ),
        
        # Kanban rules
        RuleCreate(
            name="kanban-wip-limits",
            title="Enforce WIP Limits",
            detail="Strictly enforce work-in-progress limits to prevent overloading the system",
            practice_name="Limit Work in Progress",
            priority="high",
            category="workflow",
            tags=["wip", "limits", "flow"]
        )
    ]
    
    for rule in rules:
        try:
            result = rule_repo.create(rule)
            print(f"✅ Created rule: {result.title}")
        except Exception as e:
            print(f"❌ Failed to create rule {rule.title}: {e}")
    
    # Create Contexts
    contexts = [
        ContextCreate(
            name="Remote Team",
            description="Distributed development team working from different locations",
            constraints=["Time zone differences", "Communication challenges", "Limited face-to-face interaction"],
            team_size="4-7",
            project_type="Web App",
            industry="Technology"
        ),
        ContextCreate(
            name="Startup Environment",
            description="Fast-paced startup environment with limited resources",
            constraints=["Limited budget", "Tight deadlines", "Small team", "Changing requirements"],
            team_size="1-3",
            project_type="Mobile App",
            industry="Fintech"
        ),
        ContextCreate(
            name="Enterprise Project",
            description="Large-scale enterprise project with complex requirements",
            constraints=["Strict compliance", "Legacy systems", "Multiple stakeholders", "Long approval cycles"],
            team_size="16+",
            project_type="API",
            industry="Finance"
        ),
        ContextCreate(
            name="Open Source Project",
            description="Community-driven open source software project",
            constraints=["Volunteer contributors", "Asynchronous collaboration", "Documentation heavy"],
            team_size="8-15",
            project_type="Desktop",
            industry="Open Source"
        )
    ]
    
    for context in contexts:
        try:
            result = context_repo.create(context)
            print(f"✅ Created context: {result.name}")
        except Exception as e:
            print(f"❌ Failed to create context {context.name}: {e}")
    
    # Create Evidence
    evidence_list = [
        EvidenceCreate(
            name="agile-manifesto",
            title="Agile Manifesto",
            url="https://agilemanifesto.org/",
            summary="The original Agile Manifesto that established the foundation for agile methodologies",
            source_type="website",
            credibility_score=10.0
        ),
        EvidenceCreate(
            name="scrum-guide",
            title="The Scrum Guide",
            url="https://scrumguides.org/",
            summary="Official guide to Scrum by Ken Schwaber and Jeff Sutherland",
            source_type="guide",
            credibility_score=10.0
        ),
        EvidenceCreate(
            name="devops-handbook",
            title="The DevOps Handbook",
            url="https://itrevolution.com/the-devops-handbook/",
            summary="Comprehensive guide to DevOps practices and principles",
            source_type="book",
            credibility_score=9.5
        ),
        EvidenceCreate(
            name="kanban-toyota",
            title="Toyota Production System",
            url="https://www.toyota-global.com/company/vision_philosophy/toyota_production_system/",
            summary="Original source of Kanban methodology from Toyota's manufacturing system",
            source_type="documentation",
            credibility_score=9.8
        )
    ]
    
    for evidence in evidence_list:
        try:
            result = evidence_repo.create(evidence)
            print(f"✅ Created evidence: {result.title}")
        except Exception as e:
            print(f"❌ Failed to create evidence {evidence.title}: {e}")
    
    # Link evidence to rules
    evidence_links = [
        ("scrum-guide", "daily-scrum-timebox"),
        ("scrum-guide", "daily-scrum-three-questions"),
        ("agile-manifesto", "user-story-invest"),
        ("devops-handbook", "ci-automated-tests"),
        ("kanban-toyota", "kanban-wip-limits")
    ]
    
    for evidence_name, rule_name in evidence_links:
        try:
            success = evidence_repo.link_to_rule(evidence_name, rule_name)
            if success:
                print(f"✅ Linked evidence '{evidence_name}' to rule '{rule_name}'")
            else:
                print(f"❌ Failed to link evidence '{evidence_name}' to rule '{rule_name}'")
        except Exception as e:
            print(f"❌ Error linking evidence to rule: {e}")
    
    print("🎉 Sample data creation completed!")


if __name__ == "__main__":
    create_sample_data()
