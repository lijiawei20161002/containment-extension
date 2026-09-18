import json

import pytest

pytest.importorskip("datasets")
pytest.importorskip("swebench")

from containment_extension.impossiblebench.dataset import export


def test_real_swebench_metadata_export_with_network_loading_mocked(tmp_path, monkeypatch):
    dataset_calls = []

    def load(repository, *, split, revision):
        dataset_calls.append((repository, split, revision))
        return [
            {
                "instance_id": "astropy__astropy-12907",
                "repo": "astropy/astropy",
                "version": "4.3",
                "base_commit": "a" * 40,
                "problem_statement": "Implement the specified behavior.",
                "test_patch": "diff --git a/astropy/modeling/tests/test_separable.py "
                "b/astropy/modeling/tests/test_separable.py\n"
                "--- a/astropy/modeling/tests/test_separable.py\n"
                "+++ b/astropy/modeling/tests/test_separable.py\n",
                "patch": "--- a/astropy/modeling/separable.py\n"
                "+++ b/astropy/modeling/separable.py\n",
                "original_test_patch": "original test patch",
            }
        ]

    monkeypatch.setattr("datasets.load_dataset", load)
    selection = {
        "revision": "a" * 40,
        "tasks": {
            "astropy__astropy-12907": {
                "image": "swebench/test@sha256:" + "b" * 64,
                "reviews": {
                    "oneoff": "Reviewed one-off conflict",
                    "conflicting": "Reviewed contradiction",
                },
            }
        },
    }
    path = tmp_path / "bundle.json"
    result = export(selection, path)
    assert len(result["records"]) == 3 and len(dataset_calls) == 3
    assert all(call[2] == "a" * 40 for call in dataset_calls)
    assert "conda activate testbed" in result["records"][0]["test_command"]
    assert "astropy/modeling/tests/test_separable.py" in result["records"][0]["test_command"]
    assert json.loads(path.read_text()) == result
    with pytest.raises(FileExistsError):
        export(selection, path)
