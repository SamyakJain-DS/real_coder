#!/usr/bin/env python3
import dataclasses
import json
import sys
from enum import Enum
from pathlib import Path
from typing import List


class TestStatus(Enum):
    """The test status enum."""
    PASSED = 1
    FAILED = 2
    SKIPPED = 3
    ERROR = 4


@dataclasses.dataclass
class TestResult:
    """The test result dataclass."""
    name: str
    status: TestStatus


### DO NOT MODIFY THE CODE ABOVE ###
### Implement the parsing logic below ###
 
def _extract_specs(suite: dict, path_parts: List[str]) -> List[TestResult]:
    """
    Recursively walk a Playwright JSON-reporter suite tree and return one
    TestResult per test() call (spec).
    """
    results = []
 
    title = suite.get("title", "")
    current_parts = path_parts + [title] if title else path_parts
 
    for spec in suite.get("specs", []):
        test_name = " > ".join(current_parts + [spec["title"]])
 
        if spec.get("ok", False):
            status = TestStatus.PASSED
        else:
            all_results = [
                r
                for t in spec.get("tests", [])
                for r in t.get("results", [])
            ]
            if all_results and all(r.get("status") == "skipped" for r in all_results):
                status = TestStatus.SKIPPED
            else:
                status = TestStatus.FAILED
 
        results.append(TestResult(name=test_name, status=status))
 
    for child in suite.get("suites", []):
        results.extend(_extract_specs(child, current_parts))
 
    return results
 
 
def parse_test_output(stdout_content: str, stderr_content: str) -> List[TestResult]:
    """
    Parse the JSON emitted by `playwright test --reporter=json`.
    stdout contains only the Playwright JSON (all other output is redirected
    to stderr in run.sh). Returns an empty list if the output is missing or
    unparseable (e.g. playwright failed to start on an empty repo).
    """
    content = stdout_content.strip()
    if not content:
        return []
 
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return []
 
    results: List[TestResult] = []
    for suite in data.get("suites", []):
        results.extend(_extract_specs(suite, []))
    return results
 
### Implement the parsing logic above ###
### DO NOT MODIFY THE CODE BELOW ###


def export_to_json(results: List[TestResult], output_path: Path) -> None:
    json_results = {
        'tests': [
            {'name': result.name, 'status': result.status.name} for result in results
        ]
    }
    with open(output_path, 'w') as f:
        json.dump(json_results, f, indent=2)


def main(stdout_path: Path, stderr_path: Path, output_path: Path) -> None:
    with open(stdout_path) as f:
        stdout_content = f.read()
    with open(stderr_path) as f:
        stderr_content = f.read()
    results = parse_test_output(stdout_content, stderr_content)
    export_to_json(results, output_path)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: python parsing.py <stdout_file> <stderr_file> <output_json>')
        sys.exit(1)
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
