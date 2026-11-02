from langchain.mcp import MCPAdapter
from langchain.agents import create_agent
import asyncio
from dotenv import load_dotenv
import os


load_dotenv()


async def main():
    async with MCPAdapter('http://127.0.0.1:8000/mcp') as adapter:
        tools = await adapter.list_tools()
        print("Available tools:", len(tools))
        agent = create_agent("openai:gpt-4.1", tools)
        result =  await agent.ainvoke({"messages": [{"role": "user", "content": "get customer with id 1"}]})
        
        print("Agent response: type", len(result))
        print("Agent response:", result)

if __name__ == "__main__":
    asyncio.run(main())