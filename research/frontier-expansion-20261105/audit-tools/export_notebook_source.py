"""Export notebook source without executing cells or copying their outputs."""
import argparse
import hashlib
import json
from pathlib import Path

MAX_BYTES = 20_000_000

def extract(raw, expected_blob=None):
    if len(raw) > MAX_BYTES:
        raise ValueError("Notebook exceeds size limit")
    blob = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
    if expected_blob and blob != expected_blob:
        raise ValueError("Git blob mismatch")
    notebook = json.loads(raw.decode("utf-8"))
    if not isinstance(notebook, dict) or not isinstance(notebook.get("cells"), list):
        raise ValueError("Notebook cells missing")
    cells = []
    outputs_omitted = 0
    for index, cell in enumerate(notebook["cells"]):
        if not isinstance(cell, dict):
            raise ValueError("Invalid cell")
        source = cell.get("source", [])
        if isinstance(source, list) and all(isinstance(s, str) for s in source):
            source = "".join(source)
        if not isinstance(source, str):
            raise ValueError("Invalid source text")
        outputs = cell.get("outputs", [])
        if not isinstance(outputs, list):
            raise ValueError("Invalid outputs")
        outputs_omitted += len(outputs)
        cells.append({"cell_index": index, "cell_type": cell.get("cell_type"), "execution_count": cell.get("execution_count"), "source_sha256": hashlib.sha256(source.encode()).hexdigest(), "source": source})
    return {"notebook_sha256": hashlib.sha256(raw).hexdigest(), "git_blob_sha1": blob, "bytes": len(raw), "executed_by_exporter": False, "outputs_omitted": outputs_omitted, "cells": cells, "limits": "Source-only static export, not source-truth, security, algorithm-fidelity or execution verification. Review source for secrets before sharing."}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--expected-blob", required=True)
    args = parser.parse_args()
    source = Path(args.input)
    if source.stat().st_size > MAX_BYTES:
        raise SystemExit("Notebook exceeds size limit")
    record = extract(source.read_bytes(), args.expected_blob)
    target = Path(args.output_dir)
    target.mkdir(parents=True, exist_ok=False)
    (target / "source-evidence.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    code = "\n\n".join("===== UNTRUSTED CODE CELL " + str(c["cell_index"]) + " =====\n" + c["source"] for c in record["cells"] if c["cell_type"] == "code")
    (target / "code-only.txt").write_text(code + "\n", encoding="utf-8")
    print(json.dumps({"git_blob_sha1": record["git_blob_sha1"], "cells": len(record["cells"]), "executed": False}))

if __name__ == "__main__":
    main()
