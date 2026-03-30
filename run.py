"""Start the WILDSCAN backend server."""
import asyncio
import sys

# Fix Windows event loop for async DB drivers
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import uvicorn

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True, loop="asyncio")
