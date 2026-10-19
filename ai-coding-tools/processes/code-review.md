# Code review

Open this file only when the task is a review of a pull request or a diff. Leave it closed for ordinary edits.

This file is the review workflow. It does not restate judgment or language checks.

| Doc | Job |
|---|---|
| `processes/design-principles.md` | How to judge the design of the diff |
| `stacks/<type>/review.md` | Language and framework checklist for that stack |
| `processes/code-review.md` (this file) | How to read the PR, where to write the review, and the shape of the write-up |

## Before you judge

1. Read the pull request description and the existing review comments before the diff.
2. Skip a thread when the latest commit already fixed it. Record the skip under Prior comments. Do not re-raise it.

## What to judge

1. Judge the diff against `processes/design-principles.md`.
2. Then apply the checklist in `stacks/<type>/review.md` for each type in the expanded list from `processes/getting-started.md`.

Those stack files stay the language checklist. Do not copy them here.

## Where the write-up goes

Read `project.code_reviews` from `tikal.yaml` in the workspace that keeps reviews (also `.tikal.yaml` or `tikal.json`). The value is a directory relative to that workspace root. When the key is absent, use `code-reviews`.

Write the review at `<code_reviews>/<repo>/`. Add one row under that repo in `<code_reviews>/summary.md`. The row names the pull request and points at the write-up.

Leave the service checkout untouched. Do not commit the review into the repository under review. Do not put the write-up inside `ai-coding-tools/`.

## Shape of the write-up

Use this order:

1. **Metadata** — repo, pull request, commit, date.
2. **What holds up** — what the diff already gets right.
3. **Findings** — each finding names a file and a line.
4. **Prior comments** — threads already on the pull request, including threads the latest commit fixed.
5. **Checklist** — `design-principles.md` first, then `stacks/<type>/review.md`, with a result for each item applied.
6. **Comments worth leaving** — comments still worth posting. Omit anything Prior comments already marked fixed or already said.
