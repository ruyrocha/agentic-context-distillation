import os
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Aider_Bridge")

AIDER_ENV = {
    k: v
    for k, v in {
        **os.environ,
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", ""),
        "OPENAI_API_BASE": os.environ.get("OPENAI_API_BASE", ""),
    }.items()
    if v is not None
}


@mcp.tool()
def run_aider_architect(task_description: str, target_files: list[str]) -> str:
    """
    Passes the task to Aider using an architect model for planning
    and an editor model for edits. Returns only a summary. The main
    context window never sees the raw diffs.

    ARCHITECT_MODEL and EDITOR_MODEL must include the provider prefix,
    e.g. "openai/glm-4.7" or "anthropic/claude-sonnet-4-6".
    """
    architect_model = os.environ.get("ARCHITECT_MODEL", "anthropic/claude-sonnet-4-6")
    editor_model = os.environ.get("EDITOR_MODEL", "anthropic/claude-haiku-4-5-20251001")

    files_arg = " ".join(target_files)
    command = (
        f"aider --model {architect_model} "
        f"--editor-model {editor_model} "
        f"--yes-always --no-auto-commits "
        f"--no-suggest-shell-commands "
        f"--non-interactive "
        f"--message '{task_description}' {files_arg}"
    )
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, timeout=300, env=AIDER_ENV
    )

    if result.returncode == 0:
        return "Status: Changes successfully applied to files."
    else:
        return f"Status: Error. Stderr: {result.stderr[-500:]}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
