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

import re
 
def parse_test_output(stdout_content: str, stderr_content: str) -> List[TestResult]:
    """
    Parse pytest -v output and extract individual test results.
 
    Pytest -v emits one result line per test in this format:
        tests/path/to/test_file.py::TestClass::test_name[param] STATUS [  N%]
 
    The STATUS token is one of: PASSED, FAILED, SKIPPED, ERROR.
    Parametrized test IDs (e.g. [donor_id], [kwargs0]) are part of the
    non-whitespace test-name token and are captured as-is.
    """
    results: List[TestResult] = []
    seen: set = set()
 
    status_map = {
        "PASSED":  TestStatus.PASSED,
        "FAILED":  TestStatus.FAILED,
        "SKIPPED": TestStatus.SKIPPED,
        "ERROR":   TestStatus.ERROR,
    }
 
    # Match lines produced by pytest -v during the test run:
    #   <test_id> <STATUS> [  N%]
    # <test_id> is a single non-whitespace token that includes "::" separators
    # and optional parametrize brackets, e.g.:
    #   tests/test_foo.py::TestClass::test_bar[param] PASSED [ 42%]
    pattern = re.compile(
        r"^(\S+::\S+)\s+(PASSED|FAILED|SKIPPED|ERROR)\b",
        re.MULTILINE,
    )
 
    combined = stdout_content + "\n" + stderr_content
    for match in pattern.finditer(combined):
        name = match.group(1)
        status_str = match.group(2)
        if name not in seen:
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
