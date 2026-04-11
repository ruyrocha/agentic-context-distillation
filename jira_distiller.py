import os
import httpx
from mcp.server.fastmcp import FastMCP
from anthropic import Anthropic

mcp = FastMCP("Jira_Distiller")

kwargs = {"api_key": os.environ.get("ANTHROPIC_API_KEY")}
if base_url := os.environ.get("ANTHROPIC_BASE_URL"):
    kwargs["base_url"] = base_url
client = Anthropic(**kwargs)


@mcp.tool()
def get_jira_issue_digest(issue_id: str) -> str:
    """
    Fetches a Jira issue and returns a minimal digest.
    The raw payload never reaches the main context window.
    """
    raw = httpx.get(
        f"https://your-jira.atlassian.net/rest/api/3/issue/{issue_id}",
        auth=(os.environ.get("JIRA_EMAIL"), os.environ.get("JIRA_TOKEN")),
    ).json()

    response = client.messages.create(
        model=os.environ.get("DISTILLATION_MODEL", "claude-haiku-4-5-20251001"),
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": (
                    "Extract ONLY this JSON from the Jira issue. Nothing else, no preamble:\n"
                    '{"id": "...", "status": "...", "summary": "...", '
                    '"description": "...(max 200 chars)", "last_3_comments": ["..."]}\n\n'
                    f"Raw issue:\n{raw}"
                ),
            }
        ],
    )
    return response.content[0].text


if __name__ == "__main__":
    mcp.run(transport="stdio")
