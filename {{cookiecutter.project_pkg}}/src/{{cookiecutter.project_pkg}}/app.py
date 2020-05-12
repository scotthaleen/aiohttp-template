import asyncio
import logging
from logging import Logger

from aiohttp import web
from aiohttp_swagger3 import SwaggerDocs, SwaggerUiSettings  # noqa: I201

from . import __version__, config, handler, metrics, redisapi, background_tasks

logger: Logger = logging.getLogger(__name__)


async def startup_handler(app: web.Application) -> None:
    logger.info("starting up")
    cfg = app["CONFIG"]
    app["METRICS"] = metrics.Metrics
    app["REDIS"] = await redisapi.connect(cfg["redis"]["host"], cfg["redis"]["port"])

    if cfg["background_task"]["enabled"]:
        app["TASK"] = asyncio.create_task(
            background_tasks.sample_task(
                app,
                cfg["background_task"]["name"],
                delay=cfg["background_task"]["delay"],
                startup_delay=cfg["background_task"]["startup_delay"],
            )
        )
    else:
        logger.debug("TASK is disabled")
        app["TASK"] = None


async def shutdown_handler(app: web.Application) -> None:
    logger.info("shuting down")

    try:
        if (task := app["TASK"]):
            task.cancel()
    except Exception:
        logger.exception("TASK shutdown")

    # Shutdown redis
    try:
        app["REDIS"].close()
        await app["REDIS"].wait_closed()
    except Exception:
        logger.exception("redis shutdown")

    logger.info("shutdown")


def main() -> None:
    settings = config.get_config()
    app = web.Application(
        client_max_size=5 * 1024 ** 2,
        middlewares=[handler.response_time, handler.request_counter],
    )
    swagger = SwaggerDocs(
        app,
        swagger_ui_settings=SwaggerUiSettings(path="/api/docs/"),
        title="{{cookiecutter.project_name}}",
        version=__version__,
    )
    config.init_config(app, settings)
    app.on_startup.append(startup_handler)
    app.on_cleanup.append(shutdown_handler)
    swagger.add_routes(handler.routing_table(app))
    web.run_app(
        app,
        host=settings["app"]["host"],
        port=settings["app"]["port"],  # access_log=None,
    )


if __name__ == "__main__":
    main()
