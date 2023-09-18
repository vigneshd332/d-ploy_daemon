"""
Entrypoint for the API.
"""

import json
import logging
import sys
from logging.handlers import TimedRotatingFileHandler

import uvicorn
from fastapi import Depends, FastAPI, HTTPException

from dploy_daemon.config import Settings, register_to_env
from dploy_daemon.dependencies import check_authentication, firewall_init_config
from dploy_daemon.models.daemon import RegisterRequest
from dploy_daemon.routers import config, deployments, docker, docker_compose, firewall

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
app.include_router(docker_compose.router)
app.include_router(firewall.router)


@app.get("/")
async def root() -> dict[str, str]:
    """Basic route for testing"""
    return {"message": "D-Ploy Daemon is running!"}


@app.post("/register")
async def register(request: RegisterRequest) -> dict[str, str]:
    """Register the daemon to the server"""
    if (settings.daemon_id):
        raise HTTPException(
            status_code=400, detail="Daemon already registered")
    register_to_env(request.id, request.auth_key)
    return {"message": "Success!"}

# firewall_init_config()

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "docs":
        print(json.dumps(app.openapi(), indent=4))
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000)
