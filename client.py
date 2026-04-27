import os
import asyncio
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # 1. Initialize the Claude API client
    claude = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    # 2. Configure the connection to our local MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )

    # 3. Connect to the MCP Server using Standard Input/Output
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Complete the protocol handshake
            await session.initialize()
            print("Successfully connected to the MCP Server!\n")

            # --- A. DEMONSTRATING RESOURCES ---
            print("--- 1. Fetching a Resource ---")
            resource = await session.read_resource("info://welcome-message")
            print(f"Resource Content: {resource.contents[0].text}\n")

            # --- B. DEMONSTRATING PROMPTS ---
            print("--- 2. Fetching a Prompt ---")
            prompt = await session.get_prompt("summarize_text", arguments={"text": "MCP simplifies AI integrations."})
            print(f"Prompt Template: {prompt.messages[0].content.text}\n")

            # --- C. DEMONSTRATING TOOLS WITH CLAUDE ---
            print("--- 3. Letting Claude Use a Tool ---")

            # Fetch available tools from the MCP server
            mcp_tools = await session.list_tools()

            # Format the MCP tools into Claude's expected JSON format
            claude_tools = []
            for tool in mcp_tools.tools:
                claude_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                })

            # Ask Claude a question that requires calculation
            print("Asking Claude: 'What is 452 plus 739?'")
            response = claude.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=500,
                tools=claude_tools,
                messages=[{
                    "role": "user",
                    "content": "What is 452 plus 739?"
                }]
            )

            # Check if Claude decided to use a tool to answer the question
            if response.stop_reason == "tool_use":
                # Extract the tool details from Claude's response
                tool_use = next(block for block in response.content if block.type == "tool_use")
                print(f"Claude requested to use tool: '{tool_use.name}' with inputs: {tool_use.input}")

                # Execute the tool on the local MCP server on Claude's behalf
                result = await session.call_tool(tool_use.name, arguments=tool_use.input)
                print(f"Tool Execution Result from MCP Server: {result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(main())
