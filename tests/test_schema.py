import json
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_audit_schema():
    audit = yaml.safe_load((ROOT / "examples/demo-service/audit.yml").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "plugins/greenit-audit/assets/audit.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(audit)
