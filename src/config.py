import os
from functools import lru_cache
from typing import Optional
from dataclasses import dataclass
import configparser

from src.version import __version__

import consul
from dotenv import find_dotenv, load_dotenv


@dataclass
class RedisConfig:
    HOST: Optional[str]
    PASSWORD: Optional[str]
    USERNAME: Optional[str]
    PORT: Optional[int] = 6379


@dataclass
class PostgresConfig:
    DATABASE: Optional[str]
    USERNAME: Optional[str]
    PASSWORD: Optional[str]
    HOST: Optional[str]
    PORT: Optional[int] = 5432


@dataclass
class S3Config:
    BUCKET: Optional[str]
    ENDPOINT_URL: Optional[str]
    REGION_NAME: Optional[str]
    AWS_ACCESS_KEY_ID: Optional[str]
    AWS_SECRET_ACCESS_KEY: Optional[str]
    SERVICE_NAME: Optional[str] = "s3"


@dataclass
class DbConfig:
    POSTGRESQL: Optional[PostgresConfig]
    REDIS: Optional[RedisConfig]
    S3: Optional[S3Config]


@dataclass
class Contact:
    NAME: Optional[str]
    URL: Optional[str]
    EMAIL: Optional[str]


@dataclass
class JWT:
    ACCESS_SECRET_KEY: str
    REFRESH_SECRET_KEY: str


@dataclass
class Base:
    TITLE: Optional[str]
    DESCRIPTION: Optional[str]
    VERSION: Optional[str]
    JWT: JWT
    CONTACT: Contact


@dataclass
class Config:
    DEBUG: bool
    IS_SECURE_COOKIE: bool
    BASE: Base
    DB: DbConfig


def str_to_bool(value: str) -> bool:
    return value.lower() in ("yes", "true", "t", "1")


@lru_cache()
def load_ini_config(path: str | os.PathLike, encoding="utf-8") -> Config:
    """
    Loads config from file

    :param path: *.ini
    :param encoding:
    :return:
    """
    config = configparser.ConfigParser()
    config.read(filenames=path, encoding=encoding)

    return Config(
        DEBUG=bool(int(os.getenv('DEBUG', 1))),
        IS_SECURE_COOKIE=bool(config["BASE"]["IS_SECURE_COOKIE"]),
        BASE=Base(
            TITLE=config["BASE"]["TITLE"],
            DESCRIPTION=config["BASE"]["DESCRIPTION"],
            VERSION=__version__,
            CONTACT=Contact(
                NAME=config["CONTACT"]["NAME"],
                URL=config["CONTACT"]["URL"],
                EMAIL=config["CONTACT"]["EMAIL"]
            ),
            JWT=JWT(
                ACCESS_SECRET_KEY=config["JWT"]["ACCESS_SECRET_KEY"],
                REFRESH_SECRET_KEY=config["JWT"]["REFRESH_SECRET_KEY"]
            )
        ),
        DB=DbConfig(
            POSTGRESQL=PostgresConfig(
                HOST=config["POSTGRESQL"]["HOST"],
                PORT=int(config["POSTGRESQL"]["PORT"]),
                USERNAME=config["POSTGRESQL"]["USERNAME"],
                PASSWORD=config["POSTGRESQL"]["PASSWORD"],
                DATABASE=config["POSTGRESQL"]["DATABASE"]
            ) if str_to_bool(config["POSTGRESQL"]["is_used"]) else None,
            REDIS=RedisConfig(
                HOST=config["REDIS"]["HOST"],
                USERNAME=config["REDIS"]["USERNAME"],
                PASSWORD=config["REDIS"]["PASSWORD"],
                PORT=int(config["REDIS"]["PORT"])
            ) if str_to_bool(config["REDIS"]["is_used"]) else None,
            S3=S3Config(
                ENDPOINT_URL=config["S3"]["ENDPOINT_URL"],
                REGION_NAME=config["S3"]["REGION_NAME"],
                AWS_ACCESS_KEY_ID=config["S3"]["AWS_ACCESS_KEY_ID"],
                AWS_SECRET_ACCESS_KEY=config["S3"]["AWS_SECRET_ACCESS_KEY"],
                BUCKET=config["S3"]["BUCKET"]
            ) if str_to_bool(config["S3"]["is_used"]) else None
        ),
    )



