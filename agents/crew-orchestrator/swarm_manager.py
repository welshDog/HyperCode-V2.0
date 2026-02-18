"""
HyperCode Swarm Manager
Handles dynamic agent swapping, crew composition, and phase transitions.
"""
from typing import List, Dict, Optional
from enum import Enum
from pydantic import BaseModel

class ProjectPhase(str, Enum):
    PLANNING = "planning"
    ARCHITECTURE = "architecture"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MAINTENANCE = "maintenance"

class AgentRole(str, Enum):
    # Core Roles (Always Active)
    ORCHESTRATOR = "broski_orchestrator"
    PROJECT_STRATEGIST = "project_strategist"
    FRONTEND_SPECIALIST = "frontend_specialist"
    BACKEND_SPECIALIST = "backend_specialist"
    QA_ENGINEER = "qa_engineer"
    DEVOPS_ENGINEER = "devops_engineer"
    SECURITY_ENGINEER = "security_engineer"
    DATABASE_ARCHITECT = "database_architect"
    SYSTEM_ARCHITECT = "system_architect"
    
    # Dynamic Roles (Polymorphic)
    MANIFEST_ENFORCER = "manifest_enforcer"
    HYPER_UX_FLOW = "hyper_ux_flow"
    HYPER_RESEARCH = "hyper_research"
    LOD_PROTOTYPER = "lod_prototyper"
    IDEA_ALCHEMIST = "idea_alchemist"
    HELIX_BIO_ARCHITECT = "helix_bio_architect"
    HYPER_NARRATOR = "hyper_narrator"
    DOC_SYNCER = "doc_syncer"
    HYPER_FLOW_DIMMER = "hyper_flow_dimmer"
    HYPERFOCUS_CATALYST = "hyperfocus_catalyst"

class CrewConfig(BaseModel):
    phase: ProjectPhase
    primary_agents: List[AgentRole]
    support_agents: List[AgentRole]
    quality_gate_keeper: AgentRole

class SwarmManager:
    def __init__(self):
        self.current_phase = ProjectPhase.PLANNING
        self.crews = self._initialize_crews()
        self.active_agents = set()
        self.activate_phase(self.current_phase)

    def _initialize_crews(self) -> Dict[ProjectPhase, CrewConfig]:
        return {
            ProjectPhase.PLANNING: CrewConfig(
                phase=ProjectPhase.PLANNING,
                primary_agents=[AgentRole.PROJECT_STRATEGIST, AgentRole.IDEA_ALCHEMIST],
                support_agents=[AgentRole.HYPER_RESEARCH, AgentRole.HYPER_NARRATOR],
                quality_gate_keeper=AgentRole.PROJECT_STRATEGIST
            ),
            ProjectPhase.ARCHITECTURE: CrewConfig(
                phase=ProjectPhase.ARCHITECTURE,
                primary_agents=[AgentRole.SYSTEM_ARCHITECT, AgentRole.DATABASE_ARCHITECT],
                support_agents=[AgentRole.SECURITY_ENGINEER, AgentRole.HELIX_BIO_ARCHITECT],
                quality_gate_keeper=AgentRole.SYSTEM_ARCHITECT
            ),
            ProjectPhase.DEVELOPMENT: CrewConfig(
                phase=ProjectPhase.DEVELOPMENT,
                primary_agents=[AgentRole.FRONTEND_SPECIALIST, AgentRole.BACKEND_SPECIALIST],
                support_agents=[AgentRole.HYPER_UX_FLOW, AgentRole.DOC_SYNCER, AgentRole.MANIFEST_ENFORCER],
                quality_gate_keeper=AgentRole.QA_ENGINEER
            ),
            ProjectPhase.TESTING: CrewConfig(
                phase=ProjectPhase.TESTING,
                primary_agents=[AgentRole.QA_ENGINEER, AgentRole.SECURITY_ENGINEER],
                support_agents=[AgentRole.HYPER_FLOW_DIMMER],
                quality_gate_keeper=AgentRole.QA_ENGINEER
            ),
            ProjectPhase.DEPLOYMENT: CrewConfig(
                phase=ProjectPhase.DEPLOYMENT,
                primary_agents=[AgentRole.DEVOPS_ENGINEER],
                support_agents=[AgentRole.DOC_SYNCER, AgentRole.HYPER_NARRATOR],
                quality_gate_keeper=AgentRole.SECURITY_ENGINEER
            )
        }

    def activate_phase(self, phase: ProjectPhase):
        """Swaps the active crew based on the phase."""
        if phase not in self.crews:
            raise ValueError(f"Unknown phase: {phase}")
        
        self.current_phase = phase
        crew = self.crews[phase]
        
        # In a real implementation, this would signal containers to wake/sleep
        # For now, we logically track active agents
        self.active_agents = set(crew.primary_agents + crew.support_agents)
        self.active_agents.add(AgentRole.ORCHESTRATOR) # Always active
        
        print(f"🔄 SWARM MANAGER: Activated Phase '{phase}'. Active Crew: {[a.value for a in self.active_agents]}")
        return crew

    def get_active_crew(self) -> List[str]:
        return [agent.value for agent in self.active_agents]

    def get_gatekeeper(self) -> str:
        return self.crews[self.current_phase].quality_gate_keeper.value

    def is_agent_active(self, agent_role: str) -> bool:
        return agent_role in [a.value for a in self.active_agents]

    def recommend_agent_for_task(self, task_description: str) -> str:
        # Simple keyword matching for demo purposes
        # In production, use LLM to classify task intent
        task_lower = task_description.lower()
        if "test" in task_lower or "bug" in task_lower:
            return AgentRole.QA_ENGINEER.value
        elif "deploy" in task_lower or "docker" in task_lower:
            return AgentRole.DEVOPS_ENGINEER.value
        elif "ui" in task_lower or "frontend" in task_lower or "css" in task_lower:
            return AgentRole.FRONTEND_SPECIALIST.value
        elif "api" in task_lower or "backend" in task_lower or "python" in task_lower:
            return AgentRole.BACKEND_SPECIALIST.value
        elif "db" in task_lower or "schema" in task_lower:
            return AgentRole.DATABASE_ARCHITECT.value
        elif "security" in task_lower or "auth" in task_lower:
            return AgentRole.SECURITY_ENGINEER.value
        elif "plan" in task_lower or "strategy" in task_lower:
            return AgentRole.PROJECT_STRATEGIST.value
        elif "arch" in task_lower or "system" in task_lower:
            return AgentRole.SYSTEM_ARCHITECT.value
        else:
            return AgentRole.PROJECT_STRATEGIST.value # Default to strategist
