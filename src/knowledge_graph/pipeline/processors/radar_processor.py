"""Data processor for Technology Radar items."""

from typing import Dict, List, Optional, Tuple

from loguru import logger

from ...models.nodes import MethodologyCreate, PracticeCreate, RuleCreate
from ...models.radar import RadarItem, RadarTechnique


class RadarDataProcessor:
    """Processor for Technology Radar data integration."""
    
    def __init__(self):
        """Initialize the processor."""
        self.methodology_mappings = self._init_methodology_mappings()
        self.practice_mappings = self._init_practice_mappings()
    
    def process_radar_technique(self, technique: RadarTechnique) -> Dict[str, List]:
        """Process a radar technique and generate knowledge graph entities.
        
        Args:
            technique: RadarTechnique to process
            
        Returns:
            Dictionary with lists of generated entities
        """
        result = {
            "methodologies": [],
            "practices": [],
            "rules": [],
            "evidence": [],
            "connections": []
        }
        
        # Map technique to methodologies and practices
        methodologies, practices = self._map_technique_to_entities(technique)
        result["methodologies"].extend(methodologies)
        result["practices"].extend(practices)
        
        # Generate rules from technique
        rules = self._generate_rules_from_technique(technique)
        result["rules"].extend(rules)
        
        # Generate evidence
        evidence = self._generate_evidence_from_technique(technique)
        result["evidence"].extend(evidence)
        
        # Generate connections
        connections = self._generate_connections(technique, methodologies, practices, rules)
        result["connections"].extend(connections)
        
        logger.info(f"Processed technique '{technique.name}': "
                   f"{len(methodologies)} methodologies, {len(practices)} practices, "
                   f"{len(rules)} rules, {len(evidence)} evidence")
        
        return result
    
    def _map_technique_to_entities(self, technique: RadarTechnique) -> Tuple[List[MethodologyCreate], List[PracticeCreate]]:
        """Map a technique to existing or new methodologies and practices."""
        methodologies = []
        practices = []
        
        # Check if technique maps to known methodologies
        technique_lower = technique.name.lower()
        description_lower = technique.description.lower()
        
        # Agile/DevOps methodology detection
        if any(keyword in technique_lower or keyword in description_lower 
               for keyword in ['agile', 'devops', 'continuous', 'automation', 'testing']):
            
            if 'testing' in technique_lower or 'testing' in description_lower:
                # Map to testing practices
                if technique.ring.value in ['Adopt', 'Trial']:
                    practices.append(PracticeCreate(
                        name=f"{technique.name} Practice",
                        description=f"Implementation of {technique.name} as described in ThoughtWorks Technology Radar",
                        methodology_name="DevOps",  # Default to DevOps for technical practices
                        tools=[],
                        difficulty_level=self._map_ring_to_difficulty(technique.ring),
                        estimated_time=self._estimate_implementation_time(technique)
                    ))
        
        # Quality Assurance methodology
        if any(keyword in technique_lower for keyword in ['security', 'quality', 'testing', 'review']):
            # Check if Quality Assurance methodology exists, if not create it
            qa_methodology = MethodologyCreate(
                name="Quality Assurance",
                description="Systematic approach to ensuring software quality and security",
                origin="Software Engineering Best Practices",
                category="Quality"
            )
            methodologies.append(qa_methodology)
            
            practices.append(PracticeCreate(
                name=technique.name,
                description=technique.description[:500] + "..." if len(technique.description) > 500 else technique.description,
                methodology_name="Quality Assurance",
                tools=self._extract_tools_from_description(technique.description),
                difficulty_level=self._map_ring_to_difficulty(technique.ring),
                estimated_time=self._estimate_implementation_time(technique)
            ))
        
        return methodologies, practices
    
    def _generate_rules_from_technique(self, technique: RadarTechnique) -> List[RuleCreate]:
        """Generate rules based on the technique's adoption level and description."""
        rules = []
        
        # Generate rule based on ring
        rule_priority = self._map_ring_to_priority(technique.ring)
        
        if technique.ring.value == "Adopt":
            rule_title = f"Adopt {technique.name}"
            rule_detail = f"We feel strongly that the industry should be adopting {technique.name}. " + technique.description[:300]
        elif technique.ring.value == "Trial":
            rule_title = f"Trial {technique.name}"
            rule_detail = f"Worth pursuing {technique.name}. It is important to understand how to build up this capability. " + technique.description[:300]
        elif technique.ring.value == "Assess":
            rule_title = f"Assess {technique.name}"
            rule_detail = f"Promising technique worth exploring: {technique.name}. " + technique.description[:300]
        else:  # Hold
            rule_title = f"Use {technique.name} with Caution"
            rule_detail = f"Proceed with caution when using {technique.name}. " + technique.description[:300]
        
        # Clean up the rule detail
        if rule_detail.endswith("..."):
            rule_detail = rule_detail[:-3] + "."
        
        rules.append(RuleCreate(
            name=f"thoughtworks-{technique.name.lower().replace(' ', '-')}",
            title=rule_title,
            detail=rule_detail,
            practice_name=f"{technique.name} Practice",  # Link to generated practice
            priority=rule_priority,
            category="thoughtworks-radar",
            tags=["thoughtworks", "technology-radar", technique.quadrant.value.lower()]
        ))
        
        return rules
    
    def _generate_evidence_from_technique(self, technique: RadarTechnique) -> List[Dict]:
        """Generate evidence records for the technique."""
        evidence = []
        
        if technique.source_url:
            evidence.append({
                "name": f"thoughtworks-{technique.name.lower().replace(' ', '-')}",
                "title": f"ThoughtWorks Technology Radar: {technique.name}",
                "url": str(technique.source_url),
                "summary": f"ThoughtWorks Technology Radar assessment of {technique.name} - {technique.ring.value}",
                "source_type": "technology-radar",
                "credibility_score": 8.5  # High credibility for ThoughtWorks
            })
        
        return evidence
    
    def _generate_connections(self, technique: RadarTechnique, methodologies: List, practices: List, rules: List) -> List[Dict]:
        """Generate connection information for linking entities."""
        connections = []
        
        # Connect evidence to rules
        for rule in rules:
            connections.append({
                "type": "SUPPORTED_BY",
                "from_type": "Rule",
                "from_name": rule.name,
                "to_type": "Evidence", 
                "to_name": f"thoughtworks-{technique.name.lower().replace(' ', '-')}"
            })
        
        return connections
    
    def _map_ring_to_difficulty(self, ring) -> str:
        """Map Technology Radar ring to practice difficulty level."""
        mapping = {
            "Adopt": "Beginner",
            "Trial": "Intermediate", 
            "Assess": "Advanced",
            "Hold": "Advanced"
        }
        return mapping.get(ring.value, "Intermediate")
    
    def _map_ring_to_priority(self, ring) -> str:
        """Map Technology Radar ring to rule priority."""
        mapping = {
            "Adopt": "high",
            "Trial": "medium",
            "Assess": "low", 
            "Hold": "critical"  # High priority warning
        }
        return mapping.get(ring.value, "medium")
    
    def _estimate_implementation_time(self, technique: RadarTechnique) -> str:
        """Estimate implementation time based on technique characteristics."""
        if technique.ring.value == "Adopt":
            return "1-2 weeks setup, ongoing practice"
        elif technique.ring.value == "Trial":
            return "2-4 weeks evaluation, 1-2 months implementation"
        elif technique.ring.value == "Assess":
            return "1-2 weeks research, proof of concept"
        else:  # Hold
            return "Avoid new implementation"
    
    def _extract_tools_from_description(self, description: str) -> List[str]:
        """Extract tool names from technique description."""
        tools = []
        
        # Common patterns for tool mentions
        tool_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:tool|platform|framework|library)',
            r'tools?\s+like\s+([^.]+)',
            r'using\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        
        import re
        for pattern in tool_patterns:
            matches = re.findall(pattern, description)
            for match in matches:
                if isinstance(match, str) and len(match.strip()) > 1:
                    # Clean up and split multiple tools
                    cleaned = match.strip().rstrip(',.')
                    if ',' in cleaned:
                        tools.extend([t.strip() for t in cleaned.split(',')])
                    else:
                        tools.append(cleaned)
        
        # Remove duplicates and common words
        excluded_words = {'the', 'and', 'or', 'with', 'for', 'in', 'on', 'at', 'to', 'from'}
        return [tool for tool in list(set(tools)) if tool.lower() not in excluded_words][:5]  # Limit to 5 tools
    
    def _init_methodology_mappings(self) -> Dict[str, str]:
        """Initialize mappings from techniques to methodologies."""
        return {
            "testing": "Quality Assurance",
            "security": "Quality Assurance", 
            "devops": "DevOps",
            "agile": "Agile",
            "continuous": "DevOps",
            "automation": "DevOps"
        }
    
    def _init_practice_mappings(self) -> Dict[str, str]:
        """Initialize mappings from techniques to practices."""
        return {
            "fuzz testing": "Automated Testing",
            "threat modeling": "Security Assessment",
            "api testing": "API Development",
            "monitoring": "System Monitoring"
        }
