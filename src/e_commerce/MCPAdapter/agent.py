from langchain.mcp import MCPAdapter
from langchain.agents import create_agent
from dotenv import load_dotenv

load_dotenv()

class Agent:
    def __init__(self):
        self._adapter = None
        self._agent = None
        

    @classmethod
    async def create(cls):
        self = cls()

        self._adapter = MCPAdapter("http://127.0.0.1:8000/mcp")
        await self._adapter.__aenter__()

        tools = await self._adapter.list_tools()
        self._agent = create_agent("openai:gpt-4.1-mini",tools)
        return self

    async def ask(self, prompt: str):
        response = await self._agent.ainvoke(
            {"messages": [{"role": "user","content": prompt}]}
        )

        return response["messages"][-1].content

    async def close(self):
        if self._adapter:
            await self._adapter.__aexit__(None, None, None)