#!/usr/bin/env python3
"""Main entry point for the FastAPI application."""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)