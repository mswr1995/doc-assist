from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import uvicorn

from src.api.routes import router


# create FastApi application
app = FastAPI(
    title = "DocAssist API",
    description = "Intelligent document assistant with RAG capabilities",
    version = "0.1.0",
    docs_url = "/docs", # Swagger UI at /docs
    redoc_url = "/redoc" # ReDoc UI at /redoc
)

# Add CORS middleware for web frontend support
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"], # configure appropriately for production
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# include API routes
app.include_router(router, prefix = "/api/v1")

@app.get("/")
async def root():
    """Redirect root to API documentatio"""
    return RedirectResponse(url = "/docs")

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "name": "DocAssist API",
        "version": "0.1.0",
        "description": "Intelligent document assistant with RAG capabilities",
        "endpoints": {
            "health": "/api/v1/health",
            "upload": "/api/v1/documents/upload",
            "list": "/api/v1/documents/",
            "query": "/api/v1/documents/query"
        },
        "documentation": "/docs"
    }

def main():
    """Run the FastAPI application"""
    uvicorn.run(
        "src.main:app",
        host = "0.0.0.0",
        port = 8000,
        reload = True, # auto reload on code change
        log_level = "info"
    )

if __name__ == "__main__":
    main()