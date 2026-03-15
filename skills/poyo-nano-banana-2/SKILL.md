---
name: poyo-nano-banana-2
description: Use PoYo AI's Nano Banana 2 image generation and editing models through the `https://api.poyo.ai/api/generate/submit` endpoint. Use when a user wants to generate images, edit existing images, submit Nano Banana 2 jobs, poll task status, or prepare PoYo-compatible request payloads for `nano-banana-2-new` or `nano-banana-2-new-edit`.
metadata: {"openclaw":{"homepage":"https://docs.poyo.ai/api-manual/image-series/nano-banana-2-new","requires":{"bins":["curl"],"env":["POYO_API_KEY"]},"primaryEnv":"POYO_API_KEY"}}
---

# Poyo Nano Banana 2

Use this skill to submit and track Nano Banana 2 image jobs on PoYo AI.

## Quick workflow

1. Decide which model to use:
   - `nano-banana-2-new` for text-to-image or image-guided generation
   - `nano-banana-2-new-edit` for editing existing images
2. Build the request body.
3. Submit a POST request to `https://api.poyo.ai/api/generate/submit` with Bearer auth.
4. Save the returned `task_id`.
5. Poll the unified task-status endpoint until the job finishes, or rely on `callback_url` if the user has a webhook.

## Request rules

- Require `Authorization: Bearer <POYO_API_KEY>`.
- Require top-level `model`.
- Require `input.prompt`.
- Use `input.image_urls` when the task depends on reference images or editing input.
- Keep prompts concrete and outcome-focused.
- Respect documented limits in `references/api.md`.

## Model selection

### `nano-banana-2-new`

Use for:
- text-to-image generation
- image-guided generation
- composition with reference images

### `nano-banana-2-new-edit`

Use for:
- editing an existing image
- adding, removing, or replacing scene elements
- style or composition changes based on input images

## Execution

- Read `references/api.md` for payload fields, examples, and polling notes.
- Read `references/frontend-notes.md` when you need product-side defaults or want to mirror the current desktop frontend behavior.
- Use `scripts/submit_nano_banana_2.sh` to submit a task from the shell when direct API execution is appropriate.
- If the user needs a raw curl example, adapt one from `references/api.md`.
- After submission, report the `task_id` clearly so follow-up polling is easy.

## Output expectations

When helping with a Nano Banana 2 task, include:
- chosen model
- final payload or summarized parameters
- whether reference images are used
- returned `task_id` if the request was actually submitted
- next step: poll status or wait for webhook
