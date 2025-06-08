import asyncio
from law_tool import lawPDF
import traceback
from mcp.server.fastmcp import FastMCP
import sys

mcp = FastMCP("law_tool_KOR")
law_pdf = lawPDF()

@mcp.tool()
async def pdf_url(query: str):
    try:
        results = await law_pdf.download_pdf_url(query=query)
        return results
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return f"An error occurred while searching: {str(e)}"

@mcp.tool()
async def load_pdf(query: str):
    try:
        results = await law_pdf.read_content(query=query)
        return results
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return f"An error occurred while searching: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
    