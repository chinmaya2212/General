import pytest
from app.services.vertex_llm import vertex_llm, LLMRequest, Message, VertexLLMServiceError

pytestmark = pytest.mark.asyncio

async def test_mock_llm_response():
    # Force mock pipeline isolating configurations
    vertex_llm.enabled = False
    req = LLMRequest(
        messages=[Message(role="user", content="Test Local Network Simulation")]
    )
    res = await vertex_llm.generate(req)
    
    assert res is not None
    assert "Mock implementation" in res.content
    assert res.input_tokens > 0  # Should evaluate split string len
    assert res.output_tokens > 0
    assert res.model_name == "mock-gemini"

async def test_llm_structured_and_tools_schema():
    req = LLMRequest(
        messages=[Message(role="user", content="Generate report")],
        structured_json=True,
        tools=[{"name": "fetch_agent", "description": "some hook"}]
    )
    
    # Asserting Pydantic rules evaluation cleanly
    assert req.structured_json == True
    assert len(req.tools) == 1
    assert req.temperature == 0.2
    
    res = await vertex_llm.generate(req)
    assert res.content == '{"status": "mocked", "message": "Success"}'
