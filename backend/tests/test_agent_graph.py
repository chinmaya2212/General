import pytest
from app.services.agent.graph import app_graph
from app.services.vertex_llm import vertex_llm, LLMResponse

pytestmark = pytest.mark.asyncio

async def test_langgraph_workflow_mocked_no_tools(monkeypatch):
    vertex_llm.enabled = False
    
    initial_state = {
        "messages": [{"role": "user", "content": "Hello agent"}],
        "tools_called": [],
        "findings": []
    }
    
    final_state = await app_graph.ainvoke(initial_state)
    
    assert final_state is not None
    assert len(final_state["messages"]) > 1
    assert final_state["messages"][-1]["role"] == "assistant"
    # End node termination because no tools invoked natively
    assert len(final_state["findings"]) == 1
    assert "Mock implementation" in final_state["final_answer"]

async def test_langgraph_workflow_mocked_tools(monkeypatch):
    # Patch vertex_llm to simulate a dynamic tool call response looping natively
    async def mock_generate(req):
        if not any(m.role == "tool" for m in req.messages):
            return LLMResponse(
                content="", 
                tool_calls=[{"name": "score_exposure", "args": {"asset_id": "asset_1"}, "id": "call_1"}],
                model_name="mock"
            )
        else:
            return LLMResponse(content="Asset examined and scored.", model_name="mock")
            
    monkeypatch.setattr(vertex_llm, "generate", mock_generate)
    
    initial_state = {
        "messages": [{"role": "user", "content": "Score asset_1 please"}],
        "tools_called": [],
        "findings": []
    }
    
    final_state = await app_graph.ainvoke(initial_state)
    
    assert len(final_state["tools_called"]) == 1
    assert final_state["tools_called"][0] == "score_exposure"
    assert "Asset examined" in final_state["final_answer"]
