import os
import sys
import json
import asyncio
from pathlib import Path
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load .env from project root (parent of true_mcp/)
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

# Official MCP Client Imports
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession

async def main():
    # 1. Initialize our standard LLM (OpenAI)
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # 2. Tell the MCP Client how to start the MCP Server
    # We use stdio to communicate between the client process and the server process
    server_script = os.path.join(os.path.dirname(__file__), "server.py")
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_script],
    )

    print("Connecting to the MCP Server over Stdio...")
    
    # 3. Connect to the Server properly over standard IO streams
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize handshakes with the server
            await session.initialize()

            # 4. Ask the server: "What tools do you have?"
            tools_response = await session.list_tools()
            
            # 5. Convert MCP-format tools into OpenAI-format tools
            openai_tools = []
            for tool in tools_response.tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })

            print(f"Server provided {len(openai_tools)} tools via MCP.")
            print("-" * 50)

            # 6. Interactive Chat Loop
            while True:
                user_input = input("\nYou: ")
                if user_input.lower() in ["exit", "quit"]:
                    break

                # Send request to the LLM with the MCP tools we discovered
                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": user_input}],
                    tools=openai_tools,
                    tool_choice="auto"
                )

                message = response.choices[0].message

                # If the LLM decides it wants to use a tool
                if message.tool_calls:
                    for tool_call in message.tool_calls:
                        func_name = tool_call.function.name
                        args = json.loads(tool_call.function.arguments)

                        print(f"[Client] Asking the MCP Server to execute '{func_name}'...")
                        
                        # 7. Ask the *MCP SERVER* to execute the tool
                        # Notice we DO NOT run the Python function ourselves here!
                        # We send a request over the protocol.
                        result = await session.call_tool(func_name, args)
                        
                        function_response = ""
                        for content in result.content:
                            if content.type == "text":
                                function_response += content.text
                                
                        print(f"[Server] Result was: {function_response}")

                        # 8. Report the server's findings back to the LLM
                        final_response = await client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "user", "content": user_input},
                                message,
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": function_response,
                                },
                            ],
                        )
                        print(f"Assistant: {final_response.choices[0].message.content}")
                else:
                    print(f"Assistant: {message.content}")

if __name__ == "__main__":
    asyncio.run(main())
