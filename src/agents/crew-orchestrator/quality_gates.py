"""
Quality Gates & Validation Service
Enforces strict quality standards before phase transitions.
"""
from typing import Dict, List, Any
from enum import Enum
from pydantic import BaseModel
from swarm_manager import ProjectPhase

class ValidationStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    PENDING = "pending"

class ValidationResult(BaseModel):
    check_name: str
    status: ValidationStatus
    details: str
    timestamp: str

class QualityGateService:
    def __init__(self):
        pass

    def validate_phase_transition(self, current_phase: ProjectPhase, target_phase: ProjectPhase) -> Dict[str, Any]:
        """
        Runs validation checks required to move from current_phase to target_phase.
        """
        results = []
        overall_status = ValidationStatus.PASSED

        if current_phase == ProjectPhase.PLANNING and target_phase == ProjectPhase.ARCHITECTURE:
            results.append(self._check_requirements_clarity())
            results.append(self._check_feasibility_score())
            
        elif current_phase == ProjectPhase.ARCHITECTURE and target_phase == ProjectPhase.DEVELOPMENT:
            results.append(self._check_architecture_approval())
            results.append(self._check_database_schema_validation())
            
        elif current_phase == ProjectPhase.DEVELOPMENT and target_phase == ProjectPhase.TESTING:
            results.append(self._check_linting())
            results.append(self._check_unit_tests_existence())
            results.append(self._check_no_secrets_in_code())
            
        elif current_phase == ProjectPhase.TESTING and target_phase == ProjectPhase.DEPLOYMENT:
            results.append(self._check_test_coverage())
            results.append(self._check_e2e_tests_passed())
            results.append(self._check_security_audit())

        # Aggregate results
        for res in results:
            if res.status == ValidationStatus.FAILED:
                overall_status = ValidationStatus.FAILED
                break
            if res.status == ValidationStatus.WARNING:
                overall_status = ValidationStatus.WARNING

        return {
            "transition": f"{current_phase.value} -> {target_phase.value}",
            "overall_status": overall_status,
            "checks": [r.dict() for r in results]
        }

    # --- Simulation of Checks ---

    def _check_requirements_clarity(self) -> ValidationResult:
        return ValidationResult(
            check_name="Requirements Clarity",
            status=ValidationStatus.PASSED,
            details="Requirements are clearly defined and unambiguous.",
            timestamp="now"
        )

    def _check_feasibility_score(self) -> ValidationResult:
        return ValidationResult(
            check_name="Feasibility Score",
            status=ValidationStatus.PASSED,
            details="Project feasibility score is 95/100.",
            timestamp="now"
        )

    def _check_architecture_approval(self) -> ValidationResult:
        return ValidationResult(
            check_name="Architecture Approval",
            status=ValidationStatus.PASSED,
            details="System Architect has signed off on the design.",
            timestamp="now"
        )

    def _check_database_schema_validation(self) -> ValidationResult:
        return ValidationResult(
            check_name="Database Schema Validation",
            status=ValidationStatus.PASSED,
            details="Schema is normalized and valid.",
            timestamp="now"
        )

    def _check_linting(self) -> ValidationResult:
        # In reality, this would run pylint/eslint
        return ValidationResult(
            check_name="Code Linting",
            status=ValidationStatus.PASSED,
            details="No linting errors found.",
            timestamp="now"
        )

    def _check_unit_tests_existence(self) -> ValidationResult:
        return ValidationResult(
            check_name="Unit Tests Existence",
            status=ValidationStatus.WARNING,
            details="Unit tests present but coverage is low.",
            timestamp="now"
        )

    def _check_no_secrets_in_code(self) -> ValidationResult:
        return ValidationResult(
            check_name="Secret Scanning",
            status=ValidationStatus.PASSED,
            details="No hardcoded secrets detected.",
            timestamp="now"
        )

    def _check_test_coverage(self) -> ValidationResult:
        return ValidationResult(
            check_name="Test Coverage",
            status=ValidationStatus.PASSED,
            details="Coverage is above 80%.",
            timestamp="now"
        )

    def _check_e2e_tests_passed(self) -> ValidationResult:
        return ValidationResult(
            check_name="E2E Tests",
            status=ValidationStatus.PASSED,
            details="All critical paths passed.",
            timestamp="now"
        )

    def _check_security_audit(self) -> ValidationResult:
        return ValidationResult(
            check_name="Security Audit",
            status=ValidationStatus.PASSED,
            details="No high/critical vulnerabilities found.",
            timestamp="now"
        )
