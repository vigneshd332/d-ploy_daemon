"""
Entrypoint for the API.
"""

import json
import logging
import sys
from logging.handlers import TimedRotatingFileHandler

import uvicorn
from fastapi import Depends, FastAPI

from dploy_daemon.config import Settings
from dploy_daemon.dependencies import check_authentication
from dploy_daemon.routers import config, deployments, docker

rotating_file_handler = TimedRotatingFileHandler("logs/d-ploy_daemon.log",
                                                 when="W0",
                                                 backupCount=48,
                                                 utc=True)

settings = Settings()
logging.basicConfig(level=settings.log_level,
                    format="%(asctime)s %(levelname)s: %(message)s",
                    handlers=[logging.StreamHandler(sys.stdout), rotating_file_handler])

app: FastAPI = FastAPI(dependencies=[Depends(check_authentication)])


app.include_router(config.router)
app.include_router(deployments.router)
app.include_router(docker.router)


@app.get("/")
async def root() -> dict[str, str]:
    """Basic route for testing"""
    return {"message": "Deploy Daemon is running!"}


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "docs":
        print(json.dumps(app.openapi(), indent=4))
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000)
