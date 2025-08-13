// Knowledge Graph Sample Data - Cypher 25 Script
// This script creates sample methodologies, practices, rules, contexts, and evidence
// Using Neo4j Cypher 25 syntax: https://neo4j.com/docs/cypher-manual/25/introduction/

// Select Cypher 25 version for all queries
CYPHER 25

// Create Methodologies
CREATE (agile:Methodology {
    name: "Agile",
    description: "Iterative development methodology focusing on collaboration, customer feedback, and rapid delivery",
    origin: "Agile Manifesto Authors",
    year_created: 2001,
    category: "Agile"
})

CREATE (scrum:Methodology {
    name: "Scrum",
    description: "Framework for developing and sustaining complex products in a complex environment",
    origin: "Ken Schwaber and Jeff Sutherland",
    year_created: 1995,
    category: "Agile"
})

CREATE (waterfall:Methodology {
    name: "Waterfall",
    description: "Sequential development process where progress flows downwards through distinct phases",
    origin: "Winston W. Royce",
    year_created: 1970,
    category: "Traditional"
})

CREATE (devops:Methodology {
    name: "DevOps",
    description: "Set of practices that combines software development and IT operations",
    origin: "Patrick Debois",
    year_created: 2009,
    category: "DevOps"
})

CREATE (kanban:Methodology {
    name: "Kanban",
    description: "Visual workflow management method for defining, managing and improving services",
    origin: "Toyota Production System",
    year_created: 1940,
    category: "Lean"
})

// Create Practices
CREATE (user_stories:Practice {
    name: "User Stories",
    description: "Short, simple descriptions of features told from the perspective of the end user",
    tools: ["Jira", "Azure DevOps", "Trello"],
    difficulty_level: "Beginner",
    estimated_time: "2-4 hours per story"
})

CREATE (sprint_planning:Practice {
    name: "Sprint Planning",
    description: "Event in Scrum where the team plans work to be performed during the sprint",
    tools: ["Jira", "Azure DevOps", "Miro"],
    difficulty_level: "Intermediate",
    estimated_time: "2-4 hours per sprint"
})

CREATE (daily_scrum:Practice {
    name: "Daily Scrum",
    description: "Daily time-boxed event for the development team to synchronize activities",
    tools: ["Teams", "Slack", "Zoom"],
    difficulty_level: "Beginner",
    estimated_time: "15 minutes daily"
})

CREATE (sprint_review:Practice {
    name: "Sprint Review",
    description: "Event where the Scrum Team and stakeholders inspect the increment",
    tools: ["Teams", "PowerPoint", "Demo environment"],
    difficulty_level: "Intermediate",
    estimated_time: "1-2 hours per sprint"
})

CREATE (sprint_retrospective:Practice {
    name: "Sprint Retrospective",
    description: "Event where the Scrum Team inspects itself and creates improvement plans",
    tools: ["Miro", "Retrium", "FunRetro"],
    difficulty_level: "Intermediate",
    estimated_time: "1-2 hours per sprint"
})

CREATE (continuous_integration:Practice {
    name: "Continuous Integration",
    description: "Practice of merging developer working copies to a shared mainline frequently",
    tools: ["Jenkins", "GitHub Actions", "Azure DevOps"],
    difficulty_level: "Advanced",
    estimated_time: "Initial setup: 1-2 weeks"
})

CREATE (infrastructure_as_code:Practice {
    name: "Infrastructure as Code",
    description: "Managing and provisioning infrastructure through machine-readable definition files",
    tools: ["Terraform", "Ansible", "CloudFormation"],
    difficulty_level: "Advanced",
    estimated_time: "Setup: 2-4 weeks"
})

CREATE (visualize_workflow:Practice {
    name: "Visualize Workflow",
    description: "Make work visible through boards and cards representing work items",
    tools: ["Kanban boards", "Jira", "Trello"],
    difficulty_level: "Beginner",
    estimated_time: "1-2 days setup"
})

CREATE (limit_wip:Practice {
    name: "Limit Work in Progress",
    description: "Constrain how much work can be in each stage of the workflow",
    tools: ["Physical boards", "Digital tools"],
    difficulty_level: "Intermediate",
    estimated_time: "Ongoing adjustment"
})

// Create Rules
CREATE (daily_scrum_timebox:Rule {
    name: "daily-scrum-timebox",
    title: "Daily Scrum Time-box",
    detail: "The Daily Scrum is time-boxed to 15 minutes regardless of team size",
    priority: "high",
    category: "timeboxing",
    tags: ["scrum", "meeting", "timebox"]
})

CREATE (daily_scrum_questions:Rule {
    name: "daily-scrum-three-questions",
    title: "Three Questions Format",
    detail: "Each team member answers: What did I do yesterday? What will I do today? What impediments are in my way?",
    priority: "high",
    category: "format",
    tags: ["scrum", "questions", "format"]
})

CREATE (sprint_capacity:Rule {
    name: "sprint-planning-capacity",
    title: "Team Capacity Planning",
    detail: "Consider team member availability, holidays, and other commitments when planning sprint capacity",
    priority: "high",
    category: "planning",
    tags: ["capacity", "planning", "team"]
})

CREATE (user_story_invest:Rule {
    name: "user-story-invest",
    title: "INVEST Criteria",
    detail: "User stories should be Independent, Negotiable, Valuable, Estimable, Small, and Testable",
    priority: "high",
    category: "quality",
    tags: ["invest", "criteria", "quality"]
})

CREATE (ci_commit_frequency:Rule {
    name: "ci-commit-frequency",
    title: "Frequent Commits",
    detail: "Developers should commit code to the main branch at least once per day",
    priority: "medium",
    category: "frequency",
    tags: ["commits", "integration", "frequency"]
})

CREATE (ci_automated_tests:Rule {
    name: "ci-automated-tests",
    title: "Automated Test Suite",
    detail: "Every commit should trigger automated tests to ensure code quality",
    priority: "critical",
    category: "testing",
    tags: ["automation", "testing", "quality"]
})

CREATE (kanban_wip_limits:Rule {
    name: "kanban-wip-limits",
    title: "Enforce WIP Limits",
    detail: "Strictly enforce work-in-progress limits to prevent overloading the system",
    priority: "high",
    category: "workflow",
    tags: ["wip", "limits", "flow"]
})

// Create Contexts
CREATE (remote_team:Context {
    name: "Remote Team",
    description: "Distributed development team working from different locations",
    constraints: ["Time zone differences", "Communication challenges", "Limited face-to-face interaction"],
    team_size: "4-7",
    project_type: "Web App",
    industry: "Technology"
})

CREATE (startup_env:Context {
    name: "Startup Environment",
    description: "Fast-paced startup environment with limited resources",
    constraints: ["Limited budget", "Tight deadlines", "Small team", "Changing requirements"],
    team_size: "1-3",
    project_type: "Mobile App",
    industry: "Fintech"
})

CREATE (enterprise_project:Context {
    name: "Enterprise Project",
    description: "Large-scale enterprise project with complex requirements",
    constraints: ["Strict compliance", "Legacy systems", "Multiple stakeholders", "Long approval cycles"],
    team_size: "16+",
    project_type: "API",
    industry: "Finance"
})

CREATE (open_source:Context {
    name: "Open Source Project",
    description: "Community-driven open source software project",
    constraints: ["Volunteer contributors", "Asynchronous collaboration", "Documentation heavy"],
    team_size: "8-15",
    project_type: "Desktop",
    industry: "Open Source"
})

// Create Evidence
CREATE (agile_manifesto:Evidence {
    name: "agile-manifesto",
    title: "Agile Manifesto",
    url: "https://agilemanifesto.org/",
    summary: "The original Agile Manifesto that established the foundation for agile methodologies",
    source_type: "website",
    credibility_score: 10.0
})

CREATE (scrum_guide:Evidence {
    name: "scrum-guide",
    title: "The Scrum Guide",
    url: "https://scrumguides.org/",
    summary: "Official guide to Scrum by Ken Schwaber and Jeff Sutherland",
    source_type: "guide",
    credibility_score: 10.0
})

CREATE (devops_handbook:Evidence {
    name: "devops-handbook",
    title: "The DevOps Handbook",
    url: "https://itrevolution.com/the-devops-handbook/",
    summary: "Comprehensive guide to DevOps practices and principles",
    source_type: "book",
    credibility_score: 9.5
})

CREATE (kanban_toyota:Evidence {
    name: "kanban-toyota",
    title: "Toyota Production System",
    url: "https://www.toyota-global.com/company/vision_philosophy/toyota_production_system/",
    summary: "Original source of Kanban methodology from Toyota's manufacturing system",
    source_type: "documentation",
    credibility_score: 9.8
})

// Create Relationships: Methodology -> Practice
MERGE (agile)-[:HAS_PRACTICE]->(user_stories)
MERGE (agile)-[:HAS_PRACTICE]->(sprint_planning)
MERGE (scrum)-[:HAS_PRACTICE]->(daily_scrum)
MERGE (scrum)-[:HAS_PRACTICE]->(sprint_review)
MERGE (scrum)-[:HAS_PRACTICE]->(sprint_retrospective)
MERGE (devops)-[:HAS_PRACTICE]->(continuous_integration)
MERGE (devops)-[:HAS_PRACTICE]->(infrastructure_as_code)
MERGE (kanban)-[:HAS_PRACTICE]->(visualize_workflow)
MERGE (kanban)-[:HAS_PRACTICE]->(limit_wip)

// Create Relationships: Practice -> Rule
MERGE (daily_scrum)-[:HAS_RULE]->(daily_scrum_timebox)
MERGE (daily_scrum)-[:HAS_RULE]->(daily_scrum_questions)
MERGE (sprint_planning)-[:HAS_RULE]->(sprint_capacity)
MERGE (user_stories)-[:HAS_RULE]->(user_story_invest)
MERGE (continuous_integration)-[:HAS_RULE]->(ci_commit_frequency)
MERGE (continuous_integration)-[:HAS_RULE]->(ci_automated_tests)
MERGE (limit_wip)-[:HAS_RULE]->(kanban_wip_limits)

// Create Relationships: Rule -> Context (APPLIES_IN)
MERGE (daily_scrum_timebox)-[:APPLIES_IN]->(remote_team)
MERGE (daily_scrum_questions)-[:APPLIES_IN]->(remote_team)
MERGE (user_story_invest)-[:APPLIES_IN]->(startup_env)
MERGE (user_story_invest)-[:APPLIES_IN]->(open_source)
MERGE (ci_automated_tests)-[:APPLIES_IN]->(enterprise_project)
MERGE (ci_commit_frequency)-[:APPLIES_IN]->(startup_env)
MERGE (kanban_wip_limits)-[:APPLIES_IN]->(remote_team)
MERGE (kanban_wip_limits)-[:APPLIES_IN]->(startup_env)

// Create Relationships: Rule -> Evidence (SUPPORTED_BY)
MERGE (daily_scrum_timebox)-[:SUPPORTED_BY]->(scrum_guide)
MERGE (daily_scrum_questions)-[:SUPPORTED_BY]->(scrum_guide)
MERGE (user_story_invest)-[:SUPPORTED_BY]->(agile_manifesto)
MERGE (ci_automated_tests)-[:SUPPORTED_BY]->(devops_handbook)
MERGE (kanban_wip_limits)-[:SUPPORTED_BY]->(kanban_toyota)

// Create some additional RELATED_TO relationships for cross-references
MERGE (agile)-[:RELATED_TO]->(scrum)
MERGE (daily_scrum)-[:RELATED_TO]->(sprint_planning)
MERGE (continuous_integration)-[:RELATED_TO]->(ci_automated_tests)
MERGE (remote_team)-[:RELATED_TO]->(startup_env)

// Create indexes for better performance using Cypher 25 syntax
CREATE INDEX methodology_name_idx FOR (n:Methodology) ON (n.name);
CREATE INDEX practice_name_idx FOR (n:Practice) ON (n.name);
CREATE INDEX rule_name_idx FOR (n:Rule) ON (n.name);
CREATE INDEX context_name_idx FOR (n:Context) ON (n.name);
CREATE INDEX evidence_name_idx FOR (n:Evidence) ON (n.name);
CREATE INDEX rule_priority_idx FOR (n:Rule) ON (n.priority);
CREATE INDEX rule_category_idx FOR (n:Rule) ON (n.category);

// Create constraints for unique node names
CREATE CONSTRAINT methodology_name_unique FOR (m:Methodology) REQUIRE m.name IS UNIQUE;
CREATE CONSTRAINT practice_name_unique FOR (p:Practice) REQUIRE p.name IS UNIQUE;
CREATE CONSTRAINT rule_name_unique FOR (r:Rule) REQUIRE r.name IS UNIQUE;
CREATE CONSTRAINT context_name_unique FOR (c:Context) REQUIRE c.name IS UNIQUE;
CREATE CONSTRAINT evidence_name_unique FOR (e:Evidence) REQUIRE e.name IS UNIQUE;
