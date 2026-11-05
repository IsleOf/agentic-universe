import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from export_notebook_source import extract

class ExportTests(unittest.TestCase):
    def fixture(self, code="import math\nx = math.sqrt(4)\n"):
        return json.dumps({"cells": [{"cell_type": "code", "source": [code], "execution_count": 1, "outputs": [{"data": {"image/png": "IMAGE_PAYLOAD"}}]}]}).encode()
    def test_source_preserved(self):
        result = extract(self.fixture())
        self.assertIn("math.sqrt", result["cells"][0]["source"])
    def test_outputs_omitted(self):
        result = extract(self.fixture())
        self.assertNotIn("IMAGE_PAYLOAD", json.dumps(result))
        self.assertEqual(result["outputs_omitted"], 1)
    def test_notebook_not_executed(self):
        with tempfile.TemporaryDirectory() as temp:
            sentinel = Path(temp) / "must-not-exist"
            result = extract(self.fixture(f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('bad')"))
            self.assertFalse(sentinel.exists())
            self.assertFalse(result["executed_by_exporter"])
    def test_blob_match(self):
        raw = self.fixture()
        blob = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
        self.assertEqual(extract(raw, blob)["git_blob_sha1"], blob)
    def test_blob_mismatch(self):
        with self.assertRaises(ValueError):
            extract(self.fixture(), "0" * 40)
    def test_missing_cells(self):
        with self.assertRaises(ValueError):
            extract(b"{}")

if __name__ == "__main__":
    unittest.main()
