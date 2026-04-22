#!/usr/bin/env python3
import dataclasses
import json
import re
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
    Parse the test output content and extract test results.
    """
    import re

    combined = stdout_content + "\n" + stderr_content
    line_re = re.compile(
        r"^(\S+\.py::.*?)\s+(PASSED|FAILED|SKIPPED|ERROR)\b(?:\s+\[[^\]]*\])?\s*$"
    )
    status_map = {
        "PASSED": TestStatus.PASSED,
        "FAILED": TestStatus.FAILED,
        "SKIPPED": TestStatus.SKIPPED,
        "ERROR": TestStatus.ERROR,
    }

    results: List[TestResult] = []
    for line in combined.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = line_re.match(stripped)
        if not match:
            continue
        results.append(TestResult(name=match.group(1).strip(), status=status_map[match.group(2)]))

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
