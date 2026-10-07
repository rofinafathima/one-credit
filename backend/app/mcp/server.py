import json
import sys
from app.mcp.tools import save_digest_tool, get_saved_claims_tool, export_markdown_tool
from app.utils.logging import get_logger

logger = get_logger(__name__)

def run_mcp_server():
    """
    Reads from stdin and writes to stdout following the MCP protocol (Model Context Protocol).
    """
    logger.info("Starting MCP Server on stdio...")
    for line in sys.stdin:
        if not line.strip():
            continue
            
        try:
            req = json.loads(line)
            method = req.get("method")
            params = req.get("params", {})
            req_id = req.get("id")
            
            # Respond to notifications (no id)
            if req_id is None:
                if method == "notifications/initialized":
                    logger.info("MCP Client initialized.")
                continue
            
            result = None
            error = None
            
            if method == "initialize":
                result = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "factchecker-mcp",
                        "version": "1.0.0"
                    }
                }
            elif method == "tools/list":
                result = {
                    "tools": [
                        {
                            "name": "save_digest",
                            "description": "Save a generated digest to the database.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "date": {"type": "string", "description": "Date of the digest"},
                                    "topic": {"type": "string", "description": "Topic of the digest"},
                                    "digest": {"type": "string", "description": "Markdown content"},
                                    "verified_claims": {"type": "array", "items": {"type": "string"}}
                                },
                                "required": ["date", "topic", "digest"]
                            }
                        },
                        {
                            "name": "get_saved_claims",
                            "description": "Retrieve previously checked claims, optionally filtered by date.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "start_date": {"type": "string", "description": "ISO format start date"},
                                    "end_date": {"type": "string", "description": "ISO format end date"}
                                }
                            }
                        },
                        {
                            "name": "export_markdown",
                            "description": "Export the report as a markdown file to the exports directory.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "report_type": {"type": "string"},
                                    "content": {"type": "string"},
                                    "filename": {"type": "string"}
                                },
                                "required": ["report_type", "content", "filename"]
                            }
                        }
                    ]
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                
                tool_result = ""
                
                if tool_name == "save_digest":
                    tool_result = save_digest_tool(
                        date=tool_args.get("date"),
                        topic=tool_args.get("topic"),
                        digest=tool_args.get("digest"),
                        verified_claims=tool_args.get("verified_claims", [])
                    )
                elif tool_name == "get_saved_claims":
                    tool_result = json.dumps(get_saved_claims_tool(
                        start_date=tool_args.get("start_date"),
                        end_date=tool_args.get("end_date")
                    ))
                elif tool_name == "export_markdown":
                    tool_result = export_markdown_tool(
                        report_type=tool_args.get("report_type"),
                        content=tool_args.get("content"),
                        filename=tool_args.get("filename")
                    )
                else:
                    error = f"Unknown tool: {tool_name}"
                    
                if not error:
                    result = {
                        "content": [
                            {
                                "type": "text",
                                "text": str(tool_result)
                            }
                        ]
                    }
            else:
                error = f"Unknown method: {method}"
                
            response = {
                "jsonrpc": "2.0",
                "id": req_id
            }
            if error:
                response["error"] = {"code": -32601, "message": error}
            else:
                response["result"] = result
                
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            err = {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()
        except Exception as e:
            logger.error(f"MCP Server error: {e}")
            err = {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    run_mcp_server()
