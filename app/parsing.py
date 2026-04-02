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
 
    Pytest -v lines look like:
      tests/test_sse_broker.py::TestClass::test_name PASSED [ 12%]
      tests/test_sse_broker.py::TestClass::test_name FAILED [ 14%]
      tests/test_sse_broker.py::TestClass::test_name ERROR  [ 16%]
      tests/test_sse_broker.py::TestClass::test_name SKIPPED [ 18%]
 
    We treat ERROR as FAILED so an empty codebase (build error) still
    produces all-FAILED results in before.json.
    """
    import re
    results: List[TestResult] = []
    seen: set = set()
 
    combined = stdout_content + "\n" + stderr_content
 
    # Match lines with a test node id followed by a status keyword
    pattern = re.compile(
        r"^(tests/[^\s]+\.py::[^\s]+)\s+(PASSED|FAILED|ERROR|SKIPPED)",
        re.MULTILINE,
    )
 
    status_map = {
        "PASSED": TestStatus.PASSED,
        "FAILED": TestStatus.FAILED,
        "ERROR": TestStatus.FAILED,   # treat ERROR as FAILED for F2P purposes
        "SKIPPED": TestStatus.SKIPPED,
    }
 
    for match in pattern.finditer(combined):
        name = match.group(1)
        raw_status = match.group(2)
        if name not in seen:
            seen.add(name)
            results.append(TestResult(name=name, status=status_map[raw_status]))
 
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