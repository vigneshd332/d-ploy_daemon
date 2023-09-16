"""
Contains the global configuration for the API.
(Modify the .env file to change the values)
"""

import os
from typing import Optional

from dotenv import find_dotenv, load_dotenv
from pydantic import BaseSettings
from pathlib import Path

load_dotenv(find_dotenv())


class Settings(BaseSettings):  # pylint: disable=too-few-public-methods
    """Class for global settings"""
    daemon_id: str = os.getenv("DAEMON_ID")
    daemon_secret: str = os.getenv("DAEMON_AUTH_SECRET")
    environment: Optional[str] = os.getenv("ENVIRONMENT")
    log_level: str = os.getenv("LOGLEVEL", "WARNING").upper()
    deploy_dir: Path = Path(os.getenv("DEPLOYMENTSFOLDER", "./deployments"))

    def refresh(self) -> None:
        """
        Refreshes the settings from the environment
        """
        load_dotenv(find_dotenv())
        self.__init__()


settings = Settings()
