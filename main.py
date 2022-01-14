from asyncio.proactor_events import constants
import json
import platform
import sys
import atexit
from time import sleep, time

import psutil
import redis
from decouple import config

from util import UAC_elevate, get_temp, is_admin

node_prefix = config("NODE_PREFIX", default="NODE")
node_name = config("NODE_NAME")
full_prefix = f"{node_prefix}-{node_name}"

r = redis.Redis(
    config("ROOT_SERVER_IP"),
    config("ROOT_SERVER_PORT", cast=int),
    db=config("ROOT_SERVER_DB", cast=int),
)


def register(pipe):
    nodes = pipe.get("nodes")
    if nodes is None:
        current = []
    else:
        current = json.loads(nodes.decode("utf-8"))
    if full_prefix in current:
        print(f"Node with '{full_prefix}' name already exists")
        sys.exit(1)
    current.append(full_prefix)
    pipe.multi()
    pipe.set("nodes", json.dumps(current).encode("utf-8"))


def start():
    print(f"Started. ID is {full_prefix}")
    r.transaction(register, "nodes")

    while True:
        sleep(1)
        mem = psutil.virtual_memory()
        data = {
            "cpu_cores": psutil.cpu_count(logical=False),
            "cpu_logical_cores": psutil.cpu_count(),
            "cpu_usage_per": psutil.cpu_percent(percpu=True),
            "cpu_usage_avg": psutil.cpu_percent(),
            "cpu_temperature": get_temp(),
            "memory_usage": mem.used,
            "memory_free": mem.available,
            "memory_percent": mem.percent,
        }
        r.set(f"{full_prefix}-{time()}", ex=30, value=json.dumps(data).encode("utf-8"))


def unregister(pipe):
    print(f"Deregistering {full_prefix}")
    nodes = pipe.get("nodes")
    if nodes is None:
        return
    else:
        current = json.loads(nodes.decode("utf-8"))

    current = [n for n in current if n != full_prefix]
    pipe.multi()
    pipe.set("nodes", json.dumps(current).encode("utf-8"))


if __name__ == "__main__":
    atexit.register(r.transaction, unregister, "nodes")

    if "-a" in sys.argv and platform.system() == "Windows":
        sys.argv = [a for a in sys.argv if a != "-a"]
        UAC_elevate()
        sys.exit(0)

    if not is_admin() and platform.system() == "Windows":
        print(
            "NOT RUNNING AS ADMINISTRATOR. CPU TEMPERATURE WILL ALWAYS BE 0.\nLaunch with -a to request admin privileges."
        )

    start()