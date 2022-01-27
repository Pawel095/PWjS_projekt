import atexit
import json
import platform
import sys
from time import sleep, time

import GPUtil
import psutil
import redis
from decouple import config

from util import UAC_elevate, get_temp, is_admin

node_prefix = config("NODE_PREFIX", default="NODE")
node_name = config("NODE_NAME")
full_prefix = f"{node_prefix}-{node_name}"

unregister_on_exit = False

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
    global unregister_on_exit
    print(f"Started. ID is {full_prefix}")
    r.transaction(register, "nodes")
    unregister_on_exit = True

    while True:
        sleep(0.9)
        mem = psutil.virtual_memory()
        data = {
            "system": platform.system(),
            "cpu_cores": psutil.cpu_count(logical=False),
            "cpu_logical_cores": psutil.cpu_count(),
            "cpu_usage_per": psutil.cpu_percent(percpu=True),
            "cpu_usage_avg": psutil.cpu_percent(),
            "cpu_temperature": get_temp(),
            "memory_usage": mem.used,
            "memory_free": mem.available,
            "memory_percent": mem.percent,
            "gpus": {
                gpu.id: {
                    "usage": gpu.load * 100,
                    "memory_free": gpu.memoryFree,
                    "memory_used": gpu.memoryUsed,
                    "memory_percent": gpu.memoryUtil,
                    "name": gpu.name,
                }
                for gpu in GPUtil.getGPUs()
            },
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

def on_exit():
    if unregister_on_exit:
        r.transaction(unregister, "nodes")

if __name__ == "__main__":
    atexit.register(on_exit)

    if "-a" in sys.argv and platform.system() == "Windows":
        sys.argv = [a for a in sys.argv if a != "-a"]
        UAC_elevate()
        sys.exit(0)

    if not is_admin() and platform.system() == "Windows":
        print(
            "NOT RUNNING AS ADMINISTRATOR. CPU TEMPERATURE WILL ALWAYS BE 0.\nLaunch with -a to request admin privileges."
        )

    start()
