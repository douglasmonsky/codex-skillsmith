---
name: codex-thread-renamer
description: Review and rename Codex chats/threads by inspecting conversation context, scoring current title quality, proposing clearer names, and applying user-approved changes. Use when the user asks to rename the current Codex chat, rename the last N Codex chats, rename all accessible Codex chats, clean up chat/thread titles, review chat naming quality, or generate better Codex thread names from conversation history.
---

# Codex Thread Renamer

## Overview

Review Codex thread titles before renaming them. Inspect each target thread, score how useful the current title is, propose a better title when possible, explain the recommendation, then apply only the changes the user approves.

Use the supported Codex thread tools, not local database or app-state edits.

## Required Tools

Use the Codex app thread tools:

- `list_threads` to find target threads.
- `read_thread` to inspect recent status and turn summaries.
- `set_thread_title` to apply the final title.

If these tools are not currently loaded, search for the relevant thread tool first with `tool_search` before falling back to any other method. Do not edit hidden Codex files directly unless the user explicitly asks for unsupported storage investigation after tool-based renaming fails.

## Target Selection

Support these modes:

1. **Current chat**: identify the current thread if available from tool context. If no current thread id is exposed, call `list_threads` with a small limit and infer the current thread from recency, cwd, and visible title. If more than one candidate fits, ask the user to pick instead of guessing.
2. **Last N chats**: call `list_threads` with `limit` set to at least `N`, then process the most recent `N` returned threads. If the user says "last few", default to 5.
3. **All chats**: call `list_threads` with a high practical limit. Treat "all" as all threads returned by the supported tool. If the tool appears capped, say how many were accessible and do not claim broader coverage.

For "all chats", prefer `list_threads(limit: 50)` first unless the tool schema or prior tool output clearly supports a higher value. If a larger limit is rejected, retry with `50`, then `20` if needed, and report the accepted cap in the review. Do not fail the workflow just because the first optimistic limit was rejected.

Skip archived or pinned threads only when the user asks. Otherwise include every target returned by the tool.

## Naming Rules

Generate titles from what the thread is actually about:

- Use 3 to 8 words when possible.
- Prefer concrete nouns and project/tool names.
- Include the outcome or work type when it improves clarity, such as "Setup", "Debugging", "Dashboard Launch", "Skill Design", or "Cleanup".
- Keep titles title-case unless an existing product or command name has different casing.
- Avoid generic titles like "Help With Code", "Question About Codex", "Troubleshooting", or "New Chat".
- Avoid private data, secrets, raw IDs, student names, emails, tokens, paths containing private details, and long exact error strings.
- Preserve useful existing titles when they are already specific; do not rename only for stylistic preference.

Examples:

- `Open Design MCP Setup`
- `Codex Usage Dashboard Launch`
- `PyCharm Visibility Workflow`
- `Gaze Mission Control Debugging`
- `Codex Thread Renamer Skill`

## Quality Scoring

Score title quality on a 0 to 100 scale based on how well the title gives useful context for finding the thread later.

Use this scale:

- `90-100`: excellent; specific, durable, concise, and names the real project/tool/outcome.
- `75-89`: good; mostly clear, but missing a useful detail or slightly broad.
- `60-74`: acceptable; roughly on topic but not very searchable or specific.
- `40-59`: weak; vague, partial, misleading, or focused on an incidental detail.
- `0-39`: poor; generic, untitled, wrong topic, noise, or not useful for later retrieval.

Assign `New Quality` honestly. Do not inflate the score when the thread is too broad, too sparse, or not readable enough to name confidently.

## Review Table

Start with an introspective review before renaming. Present the recommendations as a top-level table:

| Row | Thread | Current Name | Suggested Name | Current Quality | New Quality |
| --- | --- | --- | --- | ---: | ---: |

Rules:

- Use stable row numbers for the current review.
- Put the first UUID segment or another short unique thread token in `Thread` when reviewing multiple rows. Use the full thread id internally for renaming.
- Use `No change` as `Suggested Name` when the current title is already good enough.
- Keep quality scores numeric, from 0 to 100.
- Sort by lowest `Current Quality` first unless the user asks for original recency order.
- After the table, add one short explanation per row. Explain why the current name scored that way and why the suggested name is better or why no change is recommended.
- Mention any tool cap before or immediately after the table, such as "Reviewed 20 accessible chats returned by `list_threads(limit: 50)`."

Example explanation format:

```text
Row 1: The current title is generic and does not mention the actual Open Design MCP setup work. "Open Design MCP Setup" names the tool and outcome, but the new score is 88 because the thread also includes some frontend workflow discussion.
```

## Workflow

For each target thread:

1. Read the thread with `read_thread`.
2. If the recent summary is too thin or the thread changed topics, page older turns when a cursor is available.
3. Identify the durable subject, not just the last message.
4. Score the current title with the quality scale.
5. Choose one suggested title using the naming rules, or recommend `No change`.
6. Score the suggested title honestly.
7. Present the review table and per-row explanations.
8. Ask the user what to apply unless they already gave a clear selection rule in the same prompt.
9. Apply approved changes with `set_thread_title`.

Use `includeOutputs: false` by default. Turn on truncated outputs only when summaries are not enough to understand the thread, and keep `maxOutputCharsPerItem` low.

When the user approves changes after a review:

1. Reuse the exact row-to-thread-id-to-title mapping from the latest review in the current conversation. Do not re-review unless the user asks or the prior mapping is ambiguous.
2. Resolve the user's flexible approval text against the latest row numbers and quality scores.
3. Skip rows with `Suggested Name` set to `No change`.
4. Apply approved updates with `set_thread_title`; batching or parallel calls are acceptable when the tool supports it.
5. Keep the response short while applying, but state progress for larger batches.

## Confirmation Policy

- Default to review first, then rename after user approval.
- If the user says to rename immediately, still inspect and apply only changes that are unambiguous and supported by the thread context.
- Accept flexible approval language from the user. Interpret natural requests such as:
  - `rename all`
  - `rename rows 1,3,4,5`
  - `rename anything below 70 quality`
  - `rename the ones you are confident about`
  - `skip row 2`
- Before applying, restate the selected rows briefly when the selection is complex or could be misread.
- Do not rename rows where `Suggested Name` is `No change`.
- If any proposed title is uncertain, mark it as uncertain and ask before renaming that thread.

## Verification

After applying approved renames:

- Call `list_threads` again using the same accepted scope or limit when practical.
- Confirm each renamed thread now reports the expected title.
- If a renamed thread is not returned by the verification list because of ordering or tool caps, verify it individually when a supported read or query path is available; otherwise report that it was applied but not visible in the final list.
- If any `set_thread_title` call fails or a verified title does not match, report the affected row and thread id plainly.

## Reporting

After applying changes, report:

- How many threads were inspected.
- How many were renamed.
- How many were skipped and why.
- Verification result, such as `20/20 renamed titles verified`.
- The final applied mapping for renamed rows when the set is small or when the user asks. For large batches, a few examples plus the verification count is enough.
- Any ambiguity, tool cap, or thread that could not be read.

Keep the final response concise. Do not paste full thread contents.
