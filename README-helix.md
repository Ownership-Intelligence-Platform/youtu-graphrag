# README — Helix Endpoint Summary

A concise inventory and summary of the main HTTP and other routes implemented or referenced in `backend.py`.

## Overview

This document lists the primary HTTP endpoints, WebSocket routes, static mounts, and startup hooks used by the Helix/GraphRAG backend.

## HTTP Endpoints

- GET `/` — serve frontend (`frontend/index.html`)
- GET `/api/status`
- GET `/api/datasets`
- GET `/api/graph/{dataset_name}`
- POST `/api/upload`
- POST `/api/construct-graph`
- POST `/api/ask-question`
- POST `/api/datasets/{dataset_name}/schema`
- POST `/api/datasets/{dataset_name}/reconstruct`
- DELETE `/api/datasets/{dataset_name}`

## Other routes and hooks

- WebSocket: `/ws/{client_id}`
- Static mounts: `/assets` (StaticFiles), `/frontend` (StaticFiles)
- Startup hook: `app.on_event("startup")` — initialization logic (not an HTTP endpoint)

## Counts

- Total distinct HTTP endpoints (non-static): **10**
- By HTTP method:
  - GET: **4**
  - POST: **5**
  - DELETE: **1**
- WebSocket endpoints: **1**
- Static mounts: **2**

## Notes

- An OpenAI-compatible wrapper such as `/v1/chat/completions` may also be present in `backend.py` (if added elsewhere); it is not counted above unless explicitly included.
- For debugging issues that surface as encoding/traceback rendering problems (e.g. debugpy UnicodeDecodeError), run the server with `uvicorn` in a regular terminal to capture raw stack traces:

```powershell
python -m uvicorn backend:app --host 127.0.0.1 --port 8003 --log-level debug
```
