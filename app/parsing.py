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
    import re
    results = []
    seen = set()

    pattern_std = re.compile(r'^(\S+::\S+)\s+(PASSED|FAILED|ERROR|SKIPPED)')
    pattern_xdist = re.compile(r'^\[gw\d+\]\s+\[.*?\]\s+(PASSED|FAILED|ERROR|SKIPPED)\s+(\S+::\S+)')

    for line in stdout_content.splitlines():
        line = line.strip()
        m = pattern_std.match(line)
        if m:
            name, status_str = m.group(1), m.group(2)
        else:
            m = pattern_xdist.match(line)
            if m:
                status_str, name = m.group(1), m.group(2)
            else:
                continue
        if name in seen:
            continue
        seen.add(name)
        results.append(TestResult(name=name, status=TestStatus[status_str]))

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
