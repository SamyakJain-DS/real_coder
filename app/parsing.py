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
    Parse the test output content and extract test results.
    """
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

    pytest_inline_pattern = re.compile(
        r'^(?P<name>.+::.+?)\s+(?P<status>PASSED|FAILED|SKIPPED|ERROR|XFAIL|XPASS)\s*(?:\[[^\]]+\])?$',
        re.IGNORECASE,
    )
    pytest_summary_pattern = re.compile(
        r'^(?P<status>PASSED|FAILED|SKIPPED|ERROR|XFAIL|XPASS)\s+(?P<name>.+::.+)$',
        re.IGNORECASE,
    )
    unittest_pattern = re.compile(
        r'^(?P<name>test[^\s]*\s+\([^)]+\))\s+\.\.\.\s+(?P<status>ok|FAIL|ERROR|skipped)\b',
        re.IGNORECASE,
    )

    status_map = {
        'PASSED': TestStatus.PASSED,
        'XPASS': TestStatus.PASSED,
        'FAILED': TestStatus.FAILED,
        'FAIL': TestStatus.FAILED,
        'SKIPPED': TestStatus.SKIPPED,
        'XFAIL': TestStatus.SKIPPED,
        'ERROR': TestStatus.ERROR,
        'OK': TestStatus.PASSED,
    }
    precedence = {
        TestStatus.PASSED: 0,
        TestStatus.SKIPPED: 1,
        TestStatus.FAILED: 2,
        TestStatus.ERROR: 3,
    }

    ordered_names: List[str] = []
    results_by_name: dict[str, TestStatus] = {}

    def record(name: str, status_text: str) -> None:
        cleaned_name = name.strip()
        normalized_status_text = status_text.strip().upper()
        if not cleaned_name or normalized_status_text not in status_map:
            return

        status = status_map[normalized_status_text]
        if cleaned_name not in results_by_name:
            ordered_names.append(cleaned_name)
            results_by_name[cleaned_name] = status
            return

        existing = results_by_name[cleaned_name]
        if precedence[status] > precedence[existing]:
            results_by_name[cleaned_name] = status

    combined_output = f'{stdout_content}\n{stderr_content}'
    for raw_line in combined_output.splitlines():
        line = ansi_escape.sub('', raw_line).strip()
        if not line:
            continue

        match = pytest_inline_pattern.match(line)
        if match:
            record(match.group('name'), match.group('status'))
            continue

        match = pytest_summary_pattern.match(line)
        if match:
            summary_name = match.group('name').strip()
            # Skip verbose summary lines with failure messages appended after " - ".
            if ' - ' not in summary_name:
                record(summary_name, match.group('status'))
            continue

        match = unittest_pattern.match(line)
        if match:
            record(match.group('name'), match.group('status'))

    return [TestResult(name=name, status=results_by_name[name]) for name in ordered_names]

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