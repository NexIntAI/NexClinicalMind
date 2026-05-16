"""
MCP Client — connects agents to NexClinicalMind MCP Server
Uses official MCP Python client with streamable-http transport
"""
import json
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

MCP_URL = "http://127.0.0.1:8000/mcp"

async def _call_tool_async(tool_name: str, params: dict) -> dict:
    """Call an MCP tool asynchronously using official MCP client."""
    try:
        async with streamablehttp_client(MCP_URL) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, params)
                if result.content:
                    for item in result.content:
                        if hasattr(item, "text"):
                            return json.loads(item.text)
                return {"error": "No content returned"}
    except Exception as e:
        return {"error": str(e)}

def call_mcp_tool(tool_name: str, params: dict = {}) -> dict:
    """Synchronous wrapper for async MCP tool calls."""
    try:
        return asyncio.run(_call_tool_async(tool_name, params))
    except Exception as e:
        return {"error": str(e)}

def get_pipelines_via_mcp() -> dict:
    return call_mcp_tool("get_airflow_pipeline_status")

def get_snowflake_via_mcp() -> dict:
    return call_mcp_tool("get_snowflake_data_quality")

def get_dbt_via_mcp() -> dict:
    return call_mcp_tool("get_dbt_model_status")

def rerun_pipeline_via_mcp(pipeline_id: str) -> dict:
    return call_mcp_tool("rerun_airflow_pipeline", {"pipeline_id": pipeline_id})

def lookup_regulation_via_mcp(domain: str, violation: str) -> dict:
    return call_mcp_tool("lookup_fda_regulation", {
        "cdisc_domain": domain,
        "violation_type": violation
    })

def create_audit_via_mcp(agent: str, action: str, detail: str, severity: str) -> dict:
    return call_mcp_tool("create_audit_entry", {
        "agent": agent,
        "action": action,
        "detail": detail,
        "severity": severity
    })