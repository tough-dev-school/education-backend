"""Read .env file"""
import os.path

import environ  # type: ignore

env = environ.Env(
    DEBUG=(bool, False),
    CI=(bool, False),
)
if os.path.exists(".env"):
    environ.Env.read_env(".env")  # reading .env file

__all__ = [
    "env",
]
