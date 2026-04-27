from mcp.server.fastmcp import FastMCP

# Initialize the MCP Server
mcp = FastMCP("Demo Server")

# 1. RESOURCE: Exposes static or dynamic data to the client
@mcp.resource("info://welcome-message")
def get_welcome_message() -> str:
    """A simple static welcome message."""
    return "Welcome to the Minimal MCP Server! Version 1.0"

# 2. PROMPT: Exposes reusable prompt templates
@mcp.prompt()
def summarize_text(text: str) -> str:
    """A template asking the AI to summarize text."""
    return f"Please provide a concise summary for the following text:\n\n{text}"

# 3. TOOL: Exposes executable functions that the AI can call
@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

if __name__ == "__main__":
    # Run the server using Standard I/O (stdio)
    mcp.run(transport="stdio")
