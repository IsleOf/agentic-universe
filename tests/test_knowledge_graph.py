import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.knowledge_graph import check_patch, validate_graph  # noqa: E402

GRAPH_PATH = ROOT / "knowledge/graph/agentic_universe_graph.json"
PATCH_PATH = ROOT / "evolution/proposals/2026-10-31-agent-evaluation-research-patch.json"


class KnowledgeGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
        cls.patch = json.loads(PATCH_PATH.read_text(encoding="utf-8"))

    def test_canonical_graph_has_unique_ids_and_valid_endpoints(self):
        self.assertEqual(validate_graph(self.graph), [])

    def test_research_patch_references_existing_or_proposed_nodes(self):
        base = json.loads(json.dumps(self.graph))
        proposed_node_ids = {node["id"] for node in self.patch["add_nodes"]}
        proposed_edge_ids = {edge["id"] for edge in self.patch["add_edges"]}
        graph_node_ids = {node["id"] for node in base["nodes"]}
        graph_edge_ids = {edge["id"] for edge in base["edges"]}
        self.assertTrue(proposed_node_ids.issubset(graph_node_ids))
        self.assertTrue(proposed_edge_ids.issubset(graph_edge_ids))
        base["nodes"] = [node for node in base["nodes"] if node["id"] not in proposed_node_ids]
        base["edges"] = [edge for edge in base["edges"] if edge["id"] not in proposed_edge_ids]
        self.assertEqual(check_patch(self.patch, base), [])

    def test_patch_rejects_unknown_edge_endpoint(self):
        invalid = {
            "proposal_metadata": {"id": "invalid-test"},
            "add_edges": [
                {
                    "id": "edge-invalid-test",
                    "source": "missing-source",
                    "target": "missing-target",
                    "type": "supports",
                }
            ],
        }
        errors = check_patch(invalid, self.graph)
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("unknown source" in error for error in errors))
        self.assertTrue(any("unknown target" in error for error in errors))

    def test_graph_rejects_duplicate_node_ids(self):
        duplicate = json.loads(json.dumps(self.graph))
        duplicate["nodes"].append(dict(duplicate["nodes"][0]))
        self.assertIn("Node IDs must be unique.", validate_graph(duplicate))


if __name__ == "__main__":
    unittest.main()
