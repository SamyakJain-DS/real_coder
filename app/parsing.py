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
 
def parse_test_output(stdout_content: str, stderr_content: str) -> List[TestResult]:
    import re
 
    status_map = {
        'PASSED':  TestStatus.PASSED,
        'FAILED':  TestStatus.FAILED,
        'ERROR':   TestStatus.ERROR,
        'SKIPPED': TestStatus.SKIPPED,
    }
 
    results   = []
    seen      = set()
    pending   = None          # node-id of the test whose status we are waiting for
 
    for line in stdout_content.splitlines():
        # -- Does this line begin with a pytest node-id? ------------------
        id_match = re.match(r'^(\S+::\S+)', line)
        if id_match:
            candidate = id_match.group(1)
            # Check whether the status word is already on this line
            status_inline = re.search(r'\s+(PASSED|FAILED|ERROR|SKIPPED)\b', line)
            if status_inline:
                if candidate not in seen:
                    results.append(TestResult(
                        name=candidate,
                        status=status_map[status_inline.group(1)],
                    ))
                    seen.add(candidate)
                pending = None
            else:
                # Status will appear on a later line (server log interleaved)
                pending = candidate
            continue
 
        # -- We are waiting for the status of 'pending' -------------------
        if pending is not None:
            # A bare status word at the start of a line belongs to 'pending'
            status_match = re.match(r'^(PASSED|FAILED|ERROR|SKIPPED)\b', line)
            if status_match:
                if pending not in seen:
                    results.append(TestResult(
                        name=pending,
                        status=status_map[status_match.group(1)],
                    ))
                    seen.add(pending)
                pending = None
            # Section separators or short-summary lines signal we missed the status
            elif re.match(r'^[_=]{3,}', line) or \
                 re.match(r'^(?:PASSED|FAILED|ERROR|SKIPPED)\s+\S+::', line):
                pending = None
 
    # -- Fallback: short test summary "FAILED path::class::test - reason" -
    for m in re.finditer(r'^(FAILED|ERROR)\s+(\S+::\S+)', stdout_content, re.MULTILINE):
        name = m.group(2)
        if name not in seen:
            results.append(TestResult(name=name, status=status_map[m.group(1)]))
            seen.add(name)
 
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