# Claude Code Context Firewall

A triple-firewall architecture combining Claude Code, Aider, and LLM sub-agents
to eliminate compounding cache-read costs in agentic pipelines.

## The Problem

A 30KB tool response from Jira multiplied across 200 downstream turns compounds
into millions of tokens per run. The highest cost in a long-running agentic
pipeline is not LLM generation. It is cache reads. Claude Code exposes the main
agent to raw payloads by default, and Aider cannot reach external systems to
fetch them.

## The Architecture

1. **Data Firewall:** An MCP server intercepts Jira calls, fetches the raw
   response, and routes it to a lightweight distillation model. Claude Code
   receives a 500-byte digest instead of 30KB.
2. **Coding Firewall:** A second MCP server spawns Aider as a subprocess. A
   heavy architect model handles planning via Aider repo map, while a cheap
   editor model writes the diffs. Claude Code never sees the source code.
3. **Orchestration:** Claude Code acts purely as a router. Its context stays the
   size of a short chat transcript.

## Setup

1. Install the MCP server dependencies: `pip install mcp httpx anthropic`
2. Ensure Aider is installed globally: `pip install aider-chat`
3. Copy the `.claude` folder into the root of your project repository.
4. Update `.claude/settings.json` with your API keys, base URLs, and model names
   (see Environment Variables below).
5. Start Claude Code in your project directory.

## Environment Variables

### `jira-distiller`

| Variable             | Required | Description                                                                                         |
| -------------------- | -------- | --------------------------------------------------------------------------------------------------- |
| `ANTHROPIC_API_KEY`  | Yes      | API key for the distillation model provider                                                         |
| `ANTHROPIC_BASE_URL` | No       | Override to use a non-Anthropic compatible endpoint (e.g. Z.AI). Omit to use the Anthropic default. |
| `DISTILLATION_MODEL` | No       | Model used to compress Jira payloads. Defaults to `claude-haiku-4-5-20251001`.                      |
| `JIRA_EMAIL`         | Yes      | Email used for Jira Basic Auth                                                                      |
| `JIRA_TOKEN`         | Yes      | Jira API token                                                                                      |

### `aider-bridge`

| Variable          | Required | Description                                                                                                                                                          |
| ----------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `OPENAI_API_KEY`  | Yes      | API key passed to the Aider subprocess                                                                                                                               |
| `OPENAI_API_BASE` | No       | Override to route Aider to a different endpoint. Omit to use OpenAI directly.                                                                                        |
| `ARCHITECT_MODEL` | No       | Model for high-level planning. **Must include provider prefix** (e.g. `openai/glm-4.7` or `anthropic/claude-sonnet-4-6`). Defaults to `anthropic/claude-sonnet-4-6`. |
| `EDITOR_MODEL`    | No       | Model for writing search/replace diffs. **Must include provider prefix**. Defaults to `anthropic/claude-haiku-4-5-20251001`.                                         |

## Provider Examples

**Anthropic (default)**

```json
"ANTHROPIC_API_KEY": "sk-ant-...",
"DISTILLATION_MODEL": "claude-haiku-4-5-20251001"
```

```json
"OPENAI_API_KEY": "sk-ant-...",
"OPENAI_API_BASE": "https://api.anthropic.com/v1",
"ARCHITECT_MODEL": "anthropic/claude-sonnet-4-6",
"EDITOR_MODEL": "anthropic/claude-haiku-4-5-20251001"
```

**Z.AI / GLM (cost-optimized)**

```json
"ANTHROPIC_API_KEY": "your-zai-key",
"ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic",
"DISTILLATION_MODEL": "glm-4.5-air"
```

```json
"OPENAI_API_KEY": "your-zai-key",
"OPENAI_API_BASE": "https://api.z.ai/api/openai",
"ARCHITECT_MODEL": "openai/glm-4.7",
"EDITOR_MODEL": "openai/glm-4.5-air"
```
