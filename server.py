from fastapi.responses import RedirectResponse
import uvicorn
from gptapi import app
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()

# Add middleware to handle CORS and trusted hosts
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the HTML file at the root URL
@app.get("/")
async def read_root():
    return RedirectResponse(url="/static/view.html")

if __name__ == "__main__":
    uvicorn.run(
        "gptapi:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        proxy_headers=True,
        forwarded_allow_ips="*"
    )