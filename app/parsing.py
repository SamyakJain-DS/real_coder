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

_STATUS_MAP = {
    'PASSED': TestStatus.PASSED,
    'FAILED': TestStatus.FAILED,
    'SKIPPED': TestStatus.SKIPPED,
    'ERROR': TestStatus.ERROR,
    'XPASS': TestStatus.PASSED,
    'XFAIL': TestStatus.FAILED,
}

# Pytest verbose progress lines:
#   tests/test_blink_tree.py::test_name PASSED   [ 50%]
#   tests/test_blink_tree.py::test_name[param] FAILED  [ 50%]
_PROGRESS_RE = re.compile(
    r'^(?P<name>\S+::\S+?)\s+'
    r'(?P<status>PASSED|FAILED|SKIPPED|ERROR|XPASS|XFAIL)\b'
)

# Pytest short summary block:
#   FAILED tests/test_blink_tree.py::test_name - reason
#   ERROR tests/test_blink_tree.py::test_name
_SUMMARY_RE = re.compile(
    r'^(?P<status>PASSED|FAILED|SKIPPED|ERROR|XPASS|XFAIL)\s+'
    r'(?P<name>\S+::\S+)'
)

# Strip ANSI colour escapes that pytest may emit when stdout is a TTY.
_ANSI_RE = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')


def _scan(content: str, results: dict) -> None:
    for raw in content.splitlines():
        line = _ANSI_RE.sub('', raw).rstrip()
        if not line:
            continue
        m = _PROGRESS_RE.match(line)
        if m is None:
            m = _SUMMARY_RE.match(line)
        if m is None:
            continue
        name = m.group('name')
        status = _STATUS_MAP.get(m.group('status'))
        if status is None:
            continue
        # Per-test progress lines are authoritative; do not let a later
        # short-summary line downgrade a result already recorded for the
        # same test.
        if name in results and results[name] is not status:
            # Prefer the more severe outcome so error/failure wins over
            # a stray duplicate PASSED line.
            severity = {
                TestStatus.PASSED: 0,
                TestStatus.SKIPPED: 1,
                TestStatus.FAILED: 2,
                TestStatus.ERROR: 3,
            }
            if severity[status] > severity[results[name]]:
                results[name] = status
        else:
            results[name] = status


def parse_test_output(stdout_content: str, stderr_content: str) -> List[TestResult]:
    results: dict = {}
    _scan(stdout_content or '', results)
    _scan(stderr_content or '', results)
    return [TestResult(name=n, status=s) for n, s in results.items()]

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
