from langgraph.graph import StateGraph, START, END
from app.services.agent.state import AgentState
from app.services.vertex_llm import vertex_llm, LLMRequest, Message
from app.services.agent.tools import execute_tool, AGENT_TOOLS
import logging

logger = logging.getLogger(__name__)

async def llm_node(state: AgentState):
    request = LLMRequest(
        messages=[Message(**m) for m in state.get("messages", [])],
        tools=AGENT_TOOLS
    )
    res = await vertex_llm.generate(request)
    
    new_message = {
        "role": "assistant", 
        "content": res.content, 
        "tool_calls": res.tool_calls or []
    }
    
    new_findings = []
    if res.content and not res.tool_calls:
        new_findings.append(res.content)
        
    return {"messages": [new_message], "findings": new_findings, "final_answer": res.content}

async def tool_node(state: AgentState):
    last_msg = state["messages"][-1]
    tool_calls = last_msg.get("tool_calls", [])
    
    responses = []
    new_tools = []
    for tc in tool_calls:
        name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", "")
        args = tc.get("args", {}) if isinstance(tc, dict) else getattr(tc, "args", {})
        call_id = tc.get("id", "") if isinstance(tc, dict) else getattr(tc, "id", "")
        
        output = await execute_tool(name, args)
        
        responses.append({
            "role": "tool",
            "content": f"Result from {name}: {output}",
            "tool_call_id": call_id
        })
        new_tools.append(name)
        
    return {"messages": responses, "tools_called": new_tools}

def should_continue(state: AgentState):
    last_msg = state["messages"][-1]
    tool_calls = last_msg.get("tool_calls", [])
    if tool_calls and len(tool_calls) > 0:
        return "tools"
    return END

# Construct explicitly
workflow = StateGraph(AgentState)
workflow.add_node("llm", llm_node)
workflow.add_node("tools", tool_node)
workflow.add_edge(START, "llm")
workflow.add_conditional_edges("llm", should_continue, {"tools": "tools", END: END})
workflow.add_edge("tools", "llm")

app_graph = workflow.compile()
