from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool

agent = Agent(
    'anthropic:claude-sonnet-4-6',
    tools=[duckduckgo_search_tool()],
    instructions='You are a helpful assistant with web search capabilities.',
)
