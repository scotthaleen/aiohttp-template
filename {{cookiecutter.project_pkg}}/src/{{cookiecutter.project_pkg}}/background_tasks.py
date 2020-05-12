import asyncio
import logging
from logging import Logger
from time import perf_counter
from . import redisapi, utils

logger: Logger = logging.getLogger(__name__)


async def sample_task(
    app, name: str, delay=60, startup_delay=60, exception_threshold=5
):
    redis = app["REDIS"]
    metrics = app["METRICS"]
    exception_count = 0
    logger.info("Starting Background Task: %s", name)
    await asyncio.sleep(startup_delay)
    try:
        while True:
            await asyncio.sleep(delay)
            try:
                # Read from redis or something
                logger.debug("executing a task")
                exception_count = 0
            except asyncio.CancelledError:
                # rethrow to stop
                raise
            except Exception:
                logger.exception("Task Exception")
                exception_count += 1
                logger.debug("Backing off %s", exception_count)
                await asyncio.sleep(60 * exception_count)  # backoff
                if exception_count > exception_threshold:
                    logger.warning("Stopping background task exceeded threshold")
                    break
    except asyncio.CancelledError:
        pass
    finally:
        pass
