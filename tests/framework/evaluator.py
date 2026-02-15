import re
import json
from typing import Any, Dict, List, Tuple
from .models import EvaluationCriteria, EvaluationMethod

class Evaluator:
    def evaluate(self, response: Any, criteria: List[EvaluationCriteria]) -> Tuple[bool, float, List[str]]:
        """
        Evaluate a response against a list of criteria.
        Returns: (success, score, error_messages)
        """
        total_score = 0.0
        max_score = 0.0
        errors = []
        all_passed = True

        for criterion in criteria:
            passed = False
            max_score += criterion.weight
            
            try:
                if criterion.method == EvaluationMethod.STATUS_CODE:
                    passed = self._check_status_code(response, criterion.value)
                elif criterion.method == EvaluationMethod.CONTAINS:
                    passed = self._check_contains(response, criterion.value)
                elif criterion.method == EvaluationMethod.EXACT_MATCH:
                    passed = self._check_exact_match(response, criterion.value)
                elif criterion.method == EvaluationMethod.REGEX:
                    passed = self._check_regex(response, criterion.value)
                elif criterion.method == EvaluationMethod.JSON_SCHEMA:
                    passed = self._check_json_schema(response, criterion.value)
                elif criterion.method == EvaluationMethod.LLM_EVAL:
                    # TODO: Implement LLM based evaluation
                    errors.append("LLM evaluation not yet implemented")
                    passed = False
                
                if passed:
                    total_score += criterion.weight
                else:
                    all_passed = False
                    errors.append(f"Failed criterion: {criterion.description or criterion.method} - Expected {criterion.value}")

            except Exception as e:
                all_passed = False
                errors.append(f"Evaluation error for {criterion.method}: {str(e)}")

        normalized_score = (total_score / max_score) * 100 if max_score > 0 else 0
        return all_passed, normalized_score, errors

    def _check_status_code(self, response: Any, expected: int) -> bool:
        # Assumes response object has status_code attribute (like httpx response)
        if hasattr(response, "status_code"):
            return response.status_code == expected
        return False

    def _check_contains(self, response: Any, expected: str) -> bool:
        content = self._get_content(response)
        return expected in content

    def _check_exact_match(self, response: Any, expected: Any) -> bool:
        content = self._get_content(response)
        # Try to parse content as JSON if expected is not string
        if not isinstance(expected, str) and isinstance(content, str):
            try:
                content = json.loads(content)
            except:
                pass
        return content == expected

    def _check_regex(self, response: Any, pattern: str) -> bool:
        content = self._get_content(response)
        return bool(re.search(pattern, content))

    def _check_json_schema(self, response: Any, schema: Dict) -> bool:
        try:
            import jsonschema
            content = self._get_content(response)
            if isinstance(content, str):
                content = json.loads(content)
            
            jsonschema.validate(instance=content, schema=schema)
            return True
        except ImportError:
            # Fallback for simple dict check if jsonschema not installed
            content = self._get_content(response)
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except:
                    return False
            
            if not isinstance(content, dict):
                # If content is a list, we can't validate "required" keys on the list itself
                # unless we have logic for it. For now, fail if not dict.
                return False
                
            if "required" in schema:
                for key in schema["required"]:
                    if key not in content:
                        return False
            return True
        except Exception:
            return False

    def _get_content(self, response: Any) -> str:
        if hasattr(response, "text"):
            return response.text
        if hasattr(response, "content"):
            return response.content.decode()
        if isinstance(response, (dict, list)):
            return json.dumps(response)
        return str(response)
