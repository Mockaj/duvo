from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from pydantic_ai.mcp import MCPServerStdio

from app.tools import save_search_to_csv

hn_server = MCPServerStdio('uv', args=['run', 'mcp-hackernews'])

agent = Agent(
    'anthropic:claude-sonnet-4-6',
    tools=[save_search_to_csv, duckduckgo_search_tool()],
    toolsets=[hn_server],
    instructions=(
        'You are a helpful assistant with web search capabilities '
        'and access to Hacker News. When asked about Hacker News, '
        'use the search_hackernews tool. '
        'When the user asks you to save or export search results, use the save_search_to_csv tool. '
        'After successfully saving, include the marker [DOWNLOAD:filename.csv] in your response '
        '(replacing filename.csv with the actual filename returned by the tool) '
        'so the UI can render a download button.'
    ),
)
