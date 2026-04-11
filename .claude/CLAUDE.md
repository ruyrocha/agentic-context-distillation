## Tool Routing Rules

ALWAYS use `get_jira_issue_digest` for any Jira ticket lookup. Never fetch raw
Jira API responses directly.

ALWAYS use `run_aider_architect` for any task requiring source file edits. Never
read source files or write diffs yourself. Your role is routing and
orchestration only.

After `run_aider_architect` returns, run tests with Bash and report the result.
Do not re-read the modified files to verify. Trust the status response.
