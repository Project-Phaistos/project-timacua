import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "timucua_annotation_validator", ROOT / "tools/timucua_text" / "validate.py"
)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class AnnotationValidatorTests(unittest.TestCase):
    def write_csv(self, rows, fields=None):
        tmp = tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", suffix=".csv", delete=False)
        self.addCleanup(lambda: Path(tmp.name).unlink(missing_ok=True))
        fields = fields or list(VALIDATOR.REQUIRED + VALIDATOR.OPTIONAL)
        writer = csv.DictWriter(tmp, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
        tmp.close()
        return Path(tmp.name)

    def valid_row(self, **overrides):
        row = {
            "text_id": "T1", "line_id": "L1", "token_id": "T1-L1-1",
            "source_ref": "folio-1", "diplomatic_form": "example",
            "certainty": "high", "review_status": "unreviewed",
        }
        row.update(overrides)
        return row

    def test_valid_record_passes(self):
        self.assertEqual(VALIDATOR.validate(self.write_csv([self.valid_row()])), [])

    def test_missing_required_value_fails(self):
        errors = VALIDATOR.validate(self.write_csv([self.valid_row(source_ref="")]))
        self.assertTrue(any("source_ref is required" in e for e in errors))

    def test_duplicate_token_key_fails(self):
        errors = VALIDATOR.validate(self.write_csv([
            self.valid_row(), self.valid_row(diplomatic_form="second")
        ]))
        self.assertTrue(any("duplicate token key" in e for e in errors))

    def test_invalid_certainty_fails(self):
        errors = VALIDATOR.validate(self.write_csv([self.valid_row(certainty="certain")]))
        self.assertTrue(any("invalid certainty" in e for e in errors))

    def test_unreadable_token_cannot_be_normalized(self):
        errors = VALIDATOR.validate(self.write_csv([
            self.valid_row(certainty="unreadable", normalized_form="guessed")
        ]))
        self.assertTrue(any("unreadable token must not have normalized_form" in e for e in errors))

    def test_empty_dataset_fails(self):
        errors = VALIDATOR.validate(self.write_csv([]))
        self.assertTrue(any("No annotation records found" in e for e in errors))

    def test_missing_column_fails(self):
        fields = ["text_id", "line_id", "token_id", "diplomatic_form", "certainty"]
        errors = VALIDATOR.validate(self.write_csv([], fields=fields))
        self.assertTrue(any("Missing required columns" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
