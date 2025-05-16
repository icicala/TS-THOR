from typing import Any, Dict, Iterator
from thor2timesketch.constants import AUDIT_TIMESTAMP, AUDIT_FINDING


class AuditEventsExtractor:

    @staticmethod
    def extract_findings(audit_json: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        findings = audit_json.get(AUDIT_FINDING) or []
        for finding in findings:
            timestamps = finding.get(AUDIT_TIMESTAMP)
            if isinstance(timestamps, dict) and bool(timestamps):
                yield finding