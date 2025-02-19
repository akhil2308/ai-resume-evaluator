import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.health.health_router import router as health_router
from app.resume_evaluator.resume_evaluator_router import router as resume_evaluator_router
from app.settings import logging_config,  ALLOWED_HOSTS

import logging
logging.config.dictConfig(logging_config)


app = FastAPI(
    title="AI Resume Evaluator",
    description="",
    version="1.0.0",
    docs_url="/docs",
    openapi_url = "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/v1/api/health", tags=["Health"])
app.include_router(resume_evaluator_router, prefix="/v1/api", tags=["Resume Evaluator"])


if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8000, log_level="info", reload=True)
