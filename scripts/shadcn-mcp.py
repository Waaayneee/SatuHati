import asyncio
import json
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    root=Path(__file__).resolve().parents[1]
    server=StdioServerParameters(command='cmd.exe',args=['/d','/c','npx','-y','shadcn@latest','mcp'],cwd=str(root/'apps/web'))
    async with stdio_client(server) as (read,write), ClientSession(read,write) as session:
        await session.initialize()
        tools=await session.list_tools()
        print('Connected shadcn MCP. Tools:',[t.name for t in tools.tools])
        for tool in tools.tools:
            if 'view_items' in tool.name or 'add_command' in tool.name or 'project_registries' in tool.name:
                print(tool.name,json.dumps(tool.input_schema))
        lookup=next((t for t in tools.tools if 'view_items' in t.name),None)
        if lookup:
            result=await session.call_tool(lookup.name,{'items':['@shadcn/dialog','@shadcn/dropdown-menu','@shadcn/calendar','@shadcn/button']})
            (root/'docs/shadcn-registry-reference.json').write_text(result.model_dump_json(indent=2),encoding='utf-8')
            print('Official component references saved.')


asyncio.run(main())
