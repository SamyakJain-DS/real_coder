#!/usr/bin/env python3
import dataclasses, json, sys
from enum import Enum
from pathlib import Path
from typing import List
class TestStatus(Enum):
    PASSED = 1
    FAILED = 2
    SKIPPED = 3
    ERROR = 4
@dataclasses.dataclass
class TestResult:
    name: str
    status: TestStatus
### DO NOT MODIFY THE CODE ABOVE ###
### Implement the parsing logic below ###
 
def parse_test_output(stdout_content: str, stderr_content: str) -> List[TestResult]:
    """
    Parse pytest -v output and extract individual test results.
 
    Pytest -v emits one line per test during execution in the form:
        tests/path/test_file.py::test_name[params] STATUS   [ xx%]
    where STATUS is PASSED, FAILED, ERROR, or SKIPPED.
    The regex below captures both plain and parametrized test names.
    """
    import re
 
    status_map = {
        "PASSED":  TestStatus.PASSED,
        "FAILED":  TestStatus.FAILED,
        "ERROR":   TestStatus.ERROR,
        "SKIPPED": TestStatus.SKIPPED,
    }
 
    # Match lines produced by pytest -v during test execution.
    # Group 1: full test node id (may include [param1-param2] suffix)
    # Group 2: status keyword
    pattern = re.compile(
        r"^(tests/\S+::\S+)\s+(PASSED|FAILED|ERROR|SKIPPED)",
        re.MULTILINE,
    )
 
    results = []
    seen = set()
 
    for match in pattern.finditer(stdout_content + "\n" + stderr_content):
        name = match.group(1)
        status_str = match.group(2)
        if name in seen:
            continue
        seen.add(name)
        results.append(TestResult(name=name, status=status_map[status_str]))
 
    return results
 
### Implement the parsing logic above ###
### DO NOT MODIFY THE CODE BELOW ###
def export_to_json(results: List[TestResult], output_path: Path) -> None:
    json_results = {'tests': [{'name': r.name, 'status': r.status.name} for r in results]}
    with open(output_path, 'w') as f:
        json.dump(json_results, f, indent=2)
def main(stdout_path: Path, stderr_path: Path, output_path: Path) -> None:
    with open(stdout_path) as f: stdout_content = f.read()
    with open(stderr_path) as f: stderr_content = f.read()
    results = parse_test_output(stdout_content, stderr_content)
    export_to_json(results, output_path)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(1)
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))