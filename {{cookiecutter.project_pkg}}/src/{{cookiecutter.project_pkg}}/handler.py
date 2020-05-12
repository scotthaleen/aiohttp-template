from time import perf_counter

# flake and black fight over this order
import yaml  # noqa: I201, I100
from aiohttp import web  # noqa: I201, I100

from . import __version__, redisapi, utils


"""
Swagger Help: https://swagger.io/docs/specification/describing-parameters/
"""


# Routes
async def index(request):
    return web.Response(text=__version__)


async def metrics(request):
    """
    ---
    summary: Metrics
    tags:
    - Health Check
    responses:
      "200":
        description: Returns metrics information
        content:
          application/json: {}
    """
    metrics = request.app["METRICS"]
    content = {
        "uptime": perf_counter() - metrics.START_TIME,
        "total_requsts": metrics.TOTAL_REQUESTS.value,
    }
    return web.json_response(content)


async def healthcheck(request):
    """
    ---
    summary: This end-point allow to test that service is up.
    tags:
    - Health Check
    responses:
        "200":
            description: Return "ok" text
    """
    return web.Response(text="ok")


async def redis_ping(request):
    """
    ---
    summary: Tests connection to Redis
    tags:
    - Health Check
    responses:
        "200":
            description: Return "pong" text
    """
    redis = request.app["REDIS"]
    return web.Response(text=await redis.ping())


async def list_qs(request):
    """
    ---
    summary: List all Queues
    tags:
    - Q Info
    responses:
      "200":
        description: returns dictionary of queue name and size
        content:
          application/json: {}
    """
    redis = request.app["REDIS"]
    results = await redisapi.get_all_qs(redis)
    return web.json_response(results)



async def redis_queue_size(request):
    """
    ---
    summary: Get the number of items in a Queue
    tags:
    - Q Info
    parameters:
      - in: path
        name: name
        schema:
          type: string
        required: true
        description: name for Queue
    responses:
      "200":
        description: Return count of items in Queue (0 may mean q does not exist)
        content:
          text/plain: {}
    """
    redis = request.app["REDIS"]
    name = request.match_info["name"]
    result = await redisapi.get_q_size(redis, name)
    return web.Response(text=str(result))


async def redis_queue_add(request):
    """
    ---
    summary: >
      Add an item to a specific Queue if the item exists the priority will be incremented by `priority`
      use negative priority values to decrease current priority of an id
    tags:
    - Q Info
    parameters:
      - in: path
        name: name
        schema:
          type: string
        required: true
        description: name for Queue
      - in: query
        name: item
        schema:
          type: string
        required: true
        description: queue item
      - in: query
        name: priority
        schema:
          type: integer
        description: priority when added to queue default (10)
    responses:
      "200":
        description: Return count of items in Queue (0 may mean q does not exist)
        content:
          text/plain: {}
    """
    params = request.rel_url.query
    redis = request.app["REDIS"]
    name = request.match_info["name"]
    item = params.get("item")
    priority = int(params.get("priority", "10"))
    await redisapi.q_add(redis, name, item, priority)
    return web.Response(text="ok")

async def redis_queue_pop(request):
    """
    ---
    summary: >
      Pulls the lowest priority item from the Queue and returns it.
      `WARNING:` Once this item is removed from the Queue it has to be added back manually
    tags:
    - Q Info
    parameters:
      - in: path
        name: name
        schema:
          type: string
        required: true
        description: name for Queue
    responses:
      "200":
        description: >
            Return the next lowest prioirty item from the queue
        content:
          application/json: {}
      "204":
        description: Queue is empty
    """
    params = request.rel_url.query
    redis = request.app["REDIS"]
    name = request.match_info["name"]
    if (item := await redisapi.get_q_pop(redis, name)) is None:
        raise web.HTTPNoContent
    result = {"item": item}
    return web.json_response(result)

async def some_complicated_post(request):
    """
    ---
    summary: Create or add items something
    tags:
    - Create Things
    parameters:
      - in: path
        name: name
        schema:
          type: string
        required: true
        description: name of it
    requestBody:
      description: Post body
      required: true
      content:
        application/json:
          schema:
            type: array
            items:
              type: object
              properties:
                text:
                  type: string
                priority:
                  type: integer
              required:
                - text
                - priority
          examples:
            example:
              summary: Sample Entry
              value:
                - text: "foo"
                  priority: 5
                - text: "bar"
                  priority: 10
                - text: "baz"
                  priority: 1

    responses:
      "200":
        description: returns dictionary
        content:
          application/json: {}
    """
    redis = request.app["REDIS"]
    # await redisapi.something(redis, ...)
    name = request.match_info["name"]
    body = await request.json()
    response = {"example": "ok",
                "name" : name,
                "len" : len(body)}
    return web.json_response(response)


def routing_table(app):
    return [
        web.get("/", index, allow_head=False),
        web.get("/healthcheck", healthcheck, allow_head=False),
        web.get("/metrics", metrics, allow_head=False),
        web.get("/redis/ping", redis_ping, allow_head=False),
        web.get("/q", list_qs, allow_head=False),
        web.put("/q/{name}/add", redis_queue_add),
        web.get("/q/{name}/pop", redis_queue_pop, allow_head=False),
        web.post("/create/{name}", some_complicated_post),
    ]


@web.middleware
async def request_counter(request, handler):
    request.app["METRICS"].TOTAL_REQUESTS.increment()
    response = await handler(request)
    return response


@web.middleware
async def response_time(request, handler):
    start_request = perf_counter()
    response = await handler(request)
    response_time = perf_counter() - start_request
    response.headers["x-app-response-time"] = f"{response_time:.8f}"
    return response
