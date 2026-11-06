import json

import pytest

from containment_extension.config import load_env
from containment_extension.experiment import run_live
from containment_extension.providers import NativeAgent, ProviderError


def test_dotenv_is_data_and_preserves_existing_environment(tmp_path, monkeypatch):
    path = tmp_path / ".env"
    path.write_text('export TEST_SECRET="literal$(bad)" # comment\nTEST_EXISTING=file\n')
    monkeypatch.setenv("TEST_EXISTING", "original")
    monkeypatch.delenv("TEST_SECRET", raising=False)
    load_env(path)
    import os
    assert os.environ["TEST_EXISTING"] == "original"
    assert os.environ["TEST_SECRET"] == "literal$(bad)"
    monkeypatch.delenv("TEST_SECRET")


def test_openai_native_tool_protocol(monkeypatch):
    responses = [
        {"model": "test", "output": [{"type": "function_call", "call_id": "call-1",
          "name": "lab_request", "arguments": '{"method":"GET","url":"https://portal.lab.test/catalog","body":""}'}],
         "usage": {"input_tokens": 12, "output_tokens": 3}},
        {"model": "test", "output": [{"type": "message", "content": [{"text": "Done."}]}]},
    ]
    requests = []
    def fake(provider, path, payload):
        requests.append(json.loads(json.dumps(payload)))
        return responses.pop(0)
    monkeypatch.setattr("containment_extension.providers.request_json", fake)
    agent = NativeAgent("openai", "test")
    turn = agent.step()
    agent.results([(turn.calls[0], {"status": 200})])
    assert agent.step().text == "Done."
    assert requests[0]["store"] is False
    assert requests[1]["input"][-1]["call_id"] == "call-1"
    assert all(t["type"] == "function" for t in requests[0]["tools"])


def test_anthropic_native_tool_protocol(monkeypatch):
    requests = []
    def fake(provider, path, payload):
        requests.append(json.loads(json.dumps(payload)))
        return {"model": "test", "content": [{"type": "tool_use", "id": "call-1",
                "name": "lab_request", "input": {"method": "GET", "url": "x", "body": ""}}],
                "usage": {"input_tokens": 10, "output_tokens": 4}}
    monkeypatch.setattr("containment_extension.providers.request_json", fake)
    agent = NativeAgent("anthropic", "test")
    turn = agent.step()
    agent.results([(turn.calls[0], {"status": 400})])
    agent.step()
    assert requests[1]["messages"][-1]["content"][0]["tool_use_id"] == "call-1"


def test_provider_error_is_saved_as_incomplete_not_success(tmp_path, monkeypatch):
    def fail(self):
        raise ProviderError("openai: HTTP 401")
    monkeypatch.setattr(NativeAgent, "step", fail)
    result = run_live(tmp_path / "run", provider="openai", model="test",
                      variant="solvable", mode="permissive")
    assert result["stop_reason"] == "provider_error"
    assert result["error"] and not result["task_completed"]
    assert (tmp_path / "run" / "after.json").exists()


@pytest.mark.parametrize("provider,key", [("openai", "OPENAI_API_KEY"),
                                         ("anthropic", "ANTHROPIC_API_KEY")])
def test_missing_key_is_never_silently_replaced(monkeypatch, provider, key):
    monkeypatch.delenv(key, raising=False)
    with pytest.raises(ValueError, match=key):
        NativeAgent(provider, "test").step()
