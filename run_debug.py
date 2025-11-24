#!/usr/bin/env python3
"""
Run backend with debug logging enabled
"""
import os
import sys

# Enable debug logging via environment variable
os.environ['DEBUG'] = '1'
os.environ['LOG_LEVEL'] = 'DEBUG'

# Import and run the backend
if __name__ == "__main__":
    import uvicorn
    from backend import app
    
    print("=" * 60)
    print("🔧 Starting Youtu-GraphRAG Backend in DEBUG mode")
    print("=" * 60)
    print("Debug logging is ENABLED for:")
    print("  - Application core (backend.py)")
    print("  - GraphRAG constructor (models.constructor)")
    print("  - GraphRAG retriever (models.retriever)")
    print("  - Utilities (utils.*)")
    print("=" * 60)
    print()
    
    # Run with debug logging
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8003,
        log_level="info",  # uvicorn's own log level
        access_log=True
    )
