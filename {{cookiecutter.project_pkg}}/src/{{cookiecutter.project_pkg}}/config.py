import argparse
import logging
import logging.config
import os
import sys
from typing import Any, Final, List, Optional

import trafaret as t

# flake and black fight over this order
import yaml  # noqa: I201, I100
from aiohttp import web  # noqa: I201, I100

ENV_LOG_CONFIG: Final = "LOG_CONFIG"


def setup_logging(
    default_path="logging.yaml", default_level=logging.INFO, env_key=ENV_LOG_CONFIG
):

    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, "rt") as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def load_settings(path):
    with open(path, "rt") as f:
        return yaml.safe_load(f.read())


app_config = t.Dict(
    {
        t.Key("app"): t.Dict({"host": t.String(), "port": t.Int(),}),
        t.Key("redis"): t.Dict({"host": t.String(), "port": t.Int(),}),
        t.Key("background_task"): t.Dict(
            {
                "name": t.String(),
                "enabled": t.Bool(),
                "delay": t.Int(),
                "startup_delay": t.Int(),
            }
        ),
    }
)


def get_config() -> Any:
    try:
        parser = argparse.ArgumentParser(add_help=False)
        required = parser.add_argument_group("required arguments")  # noqa: F841
        optional = parser.add_argument_group("optional arguments")

        # Add back help
        optional.add_argument(
            "-h",
            "--help",
            action="help",
            default=argparse.SUPPRESS,
            help="show this help message and exit",
        )

        optional.add_argument(
            "--resources",
            type=str,
            default=os.getenv("APP_RESOURCES", f"{os.getcwd()}/resources"),
            help="Directory for application resources to be loaded",
        )

        optional.add_argument(
            "--config",
            type=str,
            default=os.getenv("APP_CONFIG", "app.yaml"),
            help="App config file name in resources directory",
        )

        optional.add_argument(
            "--logging",
            type=str,
            default=os.getenv("APP_LOGGING", "logging.yaml"),
            help="App logging files name in resources directory",
        )

        options = parser.parse_args()
        settings = load_settings(f"{options.resources}/{options.config}")
        app_config.check(settings)
        setup_logging(f"{options.resources}/{options.logging}")
        return settings

    except Exception:
        parser.print_help(sys.stderr)
        raise
    return None


def init_config(app: web.Application, config: Optional[List[str]] = None) -> None:
    app["CONFIG"] = config
