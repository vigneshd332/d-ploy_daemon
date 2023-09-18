"""
Contains the global configuration for the API.
(Modify the .env file to change the values)
"""

import os
from typing import Optional

from dotenv import find_dotenv, load_dotenv, set_key
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
    sudo_passwd: str = os.getenv("SUDO_PASSWD", "password")
    dploy_zone: str = os.getenv("DPLOY_ZONE", "dploy_zone")
    dploy_blacklist_zone: str = os.getenv(
        "DPLOY_BLACKLIST_ZONE", "dploy_blacklist")

    def refresh(self) -> None:
        """
        Refreshes the settings from the environment
        """
        load_dotenv(find_dotenv())
        self.__init__()


settings = Settings()


def register_to_env(uuid: str, secret: str) -> None:
    """
    Registers the daemon to the environment
    """
    set_key(find_dotenv(), "DAEMON_ID", uuid)
    set_key(find_dotenv(), "DAEMON_AUTH_SECRET", secret)
    os.environ["DAEMON_ID"] = uuid
    os.environ["DAEMON_AUTH_SECRET"] = secret
    settings.refresh()
