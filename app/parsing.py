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
 
def parse_test_output(stdout_content: str, stderr_content: str) -> List[TestResult]:
    """
    Parse pytest -v output and extract individual test results.
 
    Two output formats must be handled:
 
    Standard pytest -v:
        tests/test_vault.py::ClassName::test_name PASSED [  5%]
        tests/test_vault.py::ClassName::test_name FAILED [ 10%]
 
    pytest-xdist (parallel, -n auto):
        [gw0] [  5%] PASSED tests/test_vault.py::ClassName::test_name
        [gw1] [ 10%] FAILED tests/test_vault.py::ClassName::test_name
 
    The two formats differ in that xdist puts STATUS before the node_id.
    """
    import re
    results: List[TestResult] = []
    seen: set = set()
 
    status_map = {
        "PASSED":  TestStatus.PASSED,
        "FAILED":  TestStatus.FAILED,
        "ERROR":   TestStatus.ERROR,
        "SKIPPED": TestStatus.SKIPPED,
    }
 
    # Pattern 1: standard pytest -v
    #   <node_id> <STATUS> [<pct>%]
    pattern_standard = re.compile(
        r"^(\S+\.py(?:::\S+)+)\s+(PASSED|FAILED|ERROR|SKIPPED)",
        re.MULTILINE,
    )
 
    # Pattern 2: pytest-xdist
    #   [gwN] [<pct>%] <STATUS> <node_id>
    pattern_xdist = re.compile(
        r"^\[gw\d+\]\s+\[\s*\d+%\]\s+(PASSED|FAILED|ERROR|SKIPPED)\s+(\S+\.py(?:::\S+)+)",
        re.MULTILINE,
    )
 
    combined = stdout_content + "\n" + stderr_content
 
    # Try xdist format first; fall back to standard format.
    xdist_matches = list(pattern_xdist.finditer(combined))
    if xdist_matches:
        for match in xdist_matches:
            status_str = match.group(1)
            node_id    = match.group(2)
            if node_id in seen:
                continue
            seen.add(node_id)
            results.append(TestResult(name=node_id, status=status_map[status_str]))
    else:
        for match in pattern_standard.finditer(combined):
            node_id    = match.group(1)
            status_str = match.group(2)
            if node_id in seen:
                continue
            seen.add(node_id)
            results.append(TestResult(name=node_id, status=status_map[status_str]))
 
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