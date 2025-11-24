# Debug Logging Guide

This guide explains how to enable detailed debug logging in Youtu-GraphRAG.

## Quick Start

### Option 1: Run with Debug Script (Recommended)

```bash
python run_debug.py
```

This will automatically enable DEBUG logging for all application components.

### Option 2: Set Environment Variables

**Windows PowerShell:**
```powershell
$env:DEBUG="1"
$env:LOG_LEVEL="DEBUG"
python backend.py
```

**Windows CMD:**
```cmd
set DEBUG=1
set LOG_LEVEL=DEBUG
python backend.py
```

**Linux/Mac:**
```bash
export DEBUG=1
export LOG_LEVEL=DEBUG
python backend.py
```

### Option 3: Run with uvicorn directly

```bash
DEBUG=1 LOG_LEVEL=DEBUG uvicorn backend:app --host 0.0.0.0 --port 8003
```

## Logging Levels

The application supports these logging levels:
- **DEBUG**: Detailed diagnostic information (most verbose)
- **INFO**: General informational messages (default)
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical errors that may stop the application

## Component-Specific Logging

The application configures different logging levels for different components:

### Application Components (DEBUG level when enabled)
- **backend.py**: Main API endpoints and request handling
- **models.constructor**: Knowledge graph construction
- **models.retriever**: Question answering and retrieval
- **utils.\***: Utility modules (logger, document parser, etc.)

### Third-Party Libraries (Reduced noise)
- **uvicorn**: INFO level (server messages)
- **uvicorn.access**: WARNING level (access logs)
- **fastapi**: INFO level
- **httpx, urllib3**: WARNING level (HTTP client libraries)

## What You'll See in Debug Mode

When debug logging is enabled, you'll see detailed information about:

### 1. **Question Answering Process** (`ask_question`)
```
[2025-11-24 10:30:15] INFO     === Starting question answering process ===
[2025-11-24 10:30:15] INFO     Client ID: default
[2025-11-24 10:30:15] INFO     Dataset: demo
[2025-11-24 10:30:15] INFO     Question: What is the capital of France?
[2025-11-24 10:30:15] DEBUG    Graph path: output/graphs/demo_new.json
[2025-11-24 10:30:15] DEBUG    Schema path: schemas/demo.json
[2025-11-24 10:30:16] INFO     === Step 1: Question Decomposition ===
[2025-11-24 10:30:16] INFO     Decomposition complete: 2 sub-questions generated
[2025-11-24 10:30:17] INFO     === Step 2: Initial Retrieval for Sub-questions ===
[2025-11-24 10:30:17] INFO     Processing sub-question 1/2: What is France?
[2025-11-24 10:30:18] INFO       Retrieved 15 triples and 5 chunks in 0.82s
[2025-11-24 10:30:18] INFO     === Step 3: IRCoT Iterative Refinement ===
[2025-11-24 10:30:19] INFO     --- IRCoT Step 1/3 ---
[2025-11-24 10:30:20] INFO     === Final Aggregation ===
[2025-11-24 10:30:20] INFO     Final answer: Paris is the capital of France.
[2025-11-24 10:30:20] INFO     === Question answering process completed successfully ===
```

### 2. **Graph Construction**
- Entity and relation extraction progress
- Schema loading and validation
- Graph building steps
- Cache file operations

### 3. **File Upload**
- File processing details
- Encoding detection
- Content parsing
- Corpus generation

### 4. **Index Building**
- FAISS index creation
- Embedding generation
- Cache operations

### 5. **WebSocket Communications**
- Message sending/receiving
- Connection status
- Progress updates

## Log Output Location

- **Console**: All logs are displayed in the console with color coding
- **File** (optional): You can add file logging by modifying `utils/logger.py`

## Color Coding

When viewing logs in a terminal that supports ANSI colors:
- 🔵 **DEBUG**: Cyan
- 🟢 **INFO**: Green
- 🟡 **WARNING**: Yellow
- 🔴 **ERROR**: Red
- 🟣 **CRITICAL**: Magenta

## Troubleshooting

### Not seeing debug logs?

1. Verify environment variables are set:
   ```bash
   # Check in PowerShell
   echo $env:DEBUG
   echo $env:LOG_LEVEL
   ```

2. Check the startup banner - it should show:
   ```
   🔧 Debug logging enabled for application components
   ```

3. Restart the application after setting environment variables

### Too much noise from libraries?

The application automatically reduces logging from third-party libraries. If you still see too much output, you can further reduce it by editing `backend.py`:

```python
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.ERROR)
```

### Want to see library internals?

To enable debug logging for specific libraries:

```python
logging.getLogger("httpx").setLevel(logging.DEBUG)
logging.getLogger("fastapi").setLevel(logging.DEBUG)
```

## Performance Impact

Debug logging has minimal performance impact for:
- API endpoints
- Small datasets
- Single user scenarios

For production with large datasets or many users:
- Use INFO level (default)
- Consider async logging for high-throughput scenarios
- Monitor disk space if using file logging
