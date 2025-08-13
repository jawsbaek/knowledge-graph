"""Unit tests for data models."""

import pytest
from pydantic import ValidationError

from knowledge_graph.models.nodes import (
    MethodologyCreate,
    PracticeCreate,
    RuleCreate,
    ContextCreate,
    EvidenceCreate,
)


class TestMethodologyCreate:
    """Test MethodologyCreate model."""
    
    def test_valid_methodology(self) -> None:
        """Test creating a valid methodology."""
        methodology = MethodologyCreate(
            name="Agile",
            description="Agile methodology",
            origin="Agile Manifesto",
            year_created=2001,
            category="Agile"
        )
        
        assert methodology.name == "Agile"
        assert methodology.description == "Agile methodology"
        assert methodology.origin == "Agile Manifesto"
        assert methodology.year_created == 2001
        assert methodology.category == "Agile"
    
    def test_methodology_name_required(self) -> None:
        """Test that methodology name is required."""
        with pytest.raises(ValidationError) as exc_info:
            MethodologyCreate()
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "missing" and "name" in str(error) for error in errors)
    
    def test_methodology_name_length(self) -> None:
        """Test methodology name length validation."""
        # Test empty name
        with pytest.raises(ValidationError):
            MethodologyCreate(name="")
        
        # Test very long name
        with pytest.raises(ValidationError):
            MethodologyCreate(name="a" * 201)
    
    def test_methodology_year_validation(self) -> None:
        """Test year validation."""
        # Test year too early
        with pytest.raises(ValidationError):
            MethodologyCreate(name="Test", year_created=1899)
        
        # Test year too late
        with pytest.raises(ValidationError):
            MethodologyCreate(name="Test", year_created=2031)
        
        # Test valid year
        methodology = MethodologyCreate(name="Test", year_created=2000)
        assert methodology.year_created == 2000


class TestPracticeCreate:
    """Test PracticeCreate model."""
    
    def test_valid_practice(self) -> None:
        """Test creating a valid practice."""
        practice = PracticeCreate(
            name="Daily Scrum",
            description="Daily synchronization meeting",
            methodology_name="Scrum",
            tools=["Teams", "Zoom"],
            difficulty_level="Beginner",
            estimated_time="15 minutes"
        )
        
        assert practice.name == "Daily Scrum"
        assert practice.methodology_name == "Scrum"
        assert practice.tools == ["Teams", "Zoom"]
        assert practice.difficulty_level == "Beginner"
    
    def test_practice_required_fields(self) -> None:
        """Test that required fields are validated."""
        with pytest.raises(ValidationError) as exc_info:
            PracticeCreate()
        
        errors = exc_info.value.errors()
        required_fields = {"name", "methodology_name"}
        error_fields = {error["loc"][0] for error in errors if error["type"] == "missing"}
        
        assert required_fields.issubset(error_fields)


class TestRuleCreate:
    """Test RuleCreate model."""
    
    def test_valid_rule(self) -> None:
        """Test creating a valid rule."""
        rule = RuleCreate(
            name="timebox-rule",
            title="Time-box Meeting",
            detail="Keep meetings time-boxed to maintain focus",
            practice_name="Daily Scrum",
            priority="high",
            category="timeboxing",
            tags=["meeting", "timebox"]
        )
        
        assert rule.name == "timebox-rule"
        assert rule.title == "Time-box Meeting"
        assert rule.practice_name == "Daily Scrum"
        assert rule.priority == "high"
        assert rule.tags == ["meeting", "timebox"]
    
    def test_rule_required_fields(self) -> None:
        """Test that required fields are validated."""
        with pytest.raises(ValidationError) as exc_info:
            RuleCreate()
        
        errors = exc_info.value.errors()
        required_fields = {"name", "title", "detail", "practice_name"}
        error_fields = {error["loc"][0] for error in errors if error["type"] == "missing"}
        
        assert required_fields.issubset(error_fields)
    
    def test_rule_default_priority(self) -> None:
        """Test default priority value."""
        rule = RuleCreate(
            name="test-rule",
            title="Test Rule",
            detail="Test detail",
            practice_name="Test Practice"
        )
        
        assert rule.priority == "medium"


class TestContextCreate:
    """Test ContextCreate model."""
    
    def test_valid_context(self) -> None:
        """Test creating a valid context."""
        context = ContextCreate(
            name="Remote Team",
            description="Distributed team context",
            constraints=["Time zones", "Communication"],
            team_size="5-10",
            project_type="Web App",
            industry="Technology"
        )
        
        assert context.name == "Remote Team"
        assert context.constraints == ["Time zones", "Communication"]
        assert context.team_size == "5-10"
    
    def test_context_name_required(self) -> None:
        """Test that context name is required."""
        with pytest.raises(ValidationError) as exc_info:
            ContextCreate()
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "missing" and "name" in str(error) for error in errors)


class TestEvidenceCreate:
    """Test EvidenceCreate model."""
    
    def test_valid_evidence(self) -> None:
        """Test creating valid evidence."""
        evidence = EvidenceCreate(
            name="agile-manifesto",
            title="Agile Manifesto",
            url="https://agilemanifesto.org",
            summary="The foundation of agile methodologies",
            source_type="website",
            credibility_score=10.0
        )
        
        assert evidence.name == "agile-manifesto"
        assert evidence.title == "Agile Manifesto"
        assert evidence.credibility_score == 10.0
    
    def test_evidence_required_fields(self) -> None:
        """Test that required fields are validated."""
        with pytest.raises(ValidationError) as exc_info:
            EvidenceCreate()
        
        errors = exc_info.value.errors()
        required_fields = {"name", "title"}
        error_fields = {error["loc"][0] for error in errors if error["type"] == "missing"}
        
        assert required_fields.issubset(error_fields)
    
    def test_evidence_credibility_score_validation(self) -> None:
        """Test credibility score validation."""
        # Test score too low
        with pytest.raises(ValidationError):
            EvidenceCreate(
                name="test",
                title="Test",
                credibility_score=-1.0
            )
        
        # Test score too high
        with pytest.raises(ValidationError):
            EvidenceCreate(
                name="test",
                title="Test",
                credibility_score=11.0
            )
        
        # Test valid score
        evidence = EvidenceCreate(
            name="test",
            title="Test",
            credibility_score=5.5
        )
        assert evidence.credibility_score == 5.5
