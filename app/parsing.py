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

import re

_PYTEST_LINE = re.compile(
    r"^(?P<name>\S.*?::\S+?)\s+(?P<status>PASSED|FAILED|SKIPPED|ERROR|XFAIL|XPASS)"
    r"(?:\s+\[\s*\d+%\s*\])?\s*$"
)

_STATUS_MAP = {
    "PASSED": TestStatus.PASSED,
    "XPASS":  TestStatus.PASSED,
    "FAILED": TestStatus.FAILED,
    "ERROR":  TestStatus.ERROR,
    "SKIPPED": TestStatus.SKIPPED,
    "XFAIL":  TestStatus.SKIPPED,
}


def parse_test_output(stdout_content: str, stderr_content: str) -> List[TestResult]:
    results: List[TestResult] = []
    for line in stdout_content.splitlines():
        line = line.rstrip()
        if not line or line[0] in "=-_":
            continue
        m = _PYTEST_LINE.match(line)
        if not m:
            continue
        name = m.group("name").strip()
        results.append(TestResult(name=name, status=_STATUS_MAP[m.group("status")]))
    return results

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