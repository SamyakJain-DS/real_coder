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
    import glob
    import xml.etree.ElementTree as ET

    results = []
    seen = set()

    for xml_path in glob.glob("/tmp/junit-reports/TEST-*.xml"):
        try:
            root = ET.parse(xml_path).getroot()
            for tc in root.iter("testcase"):
                classname = tc.get("classname", "")
                method    = tc.get("name", "")
                full_name = f"{classname}#{method}" if classname else method
                if full_name in seen:
                    continue
                seen.add(full_name)
                if tc.find("failure") is not None or tc.find("error") is not None:
                    status = TestStatus.FAILED
                elif tc.find("skipped") is not None:
                    status = TestStatus.SKIPPED
                else:
                    status = TestStatus.PASSED
                results.append(TestResult(name=full_name, status=status))
        except Exception:
            pass

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