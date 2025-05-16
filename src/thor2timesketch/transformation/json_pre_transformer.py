from typing import Dict, Any, Iterator

from thor2timesketch.constants import LOG_VERSION, AUDIT_FINDING
from thor2timesketch.utils.audit_events_extractor import AuditEventsExtractor


class JsonPreTransformer:

    def pre_transform_thor_logs(self, valid_json: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        if LOG_VERSION in valid_json:
            yield valid_json
        elif AUDIT_FINDING in valid_json:
            for finding in  AuditEventsExtractor.extract_findings(valid_json):
                yield finding
        else:
            yield valid_json
