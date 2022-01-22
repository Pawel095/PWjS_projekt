import json
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import redis
from decouple import config

from node import Node, DataPoint

app = Flask(__name__)
Bootstrap(app)
r = redis.Redis(
    config("REDIS_SERVER_IP"),
    config("REDIS_SERVER_PORT", cast=int),
    db=config("REDIS_SERVER_DB", cast=int),
)
nodes = r.get("nodes").decode("utf-8")
nodes = json.loads(nodes)
print(nodes)


def get_data_for_node(name):
    data_keys = r.keys(f"{name}-*")
    data_keys.sort()

    data_points = []
    last_data = ''
    for key in data_keys:
        data = r.get(key).decode("utf-8")
        data = json.loads(data)
        last_data = data

        try:
            gpu_name = data['gpus']['0']['name']
            gpu_usage = data["gpus"]["0"]["usage"]
            gpu_memory_p = data["gpus"]["0"]["memory_percent"]
        except Exception:
            gpu_name = '-'
            gpu_usage = 0
            gpu_memory_p = 0

        # gpu_name = '-'
        dp = DataPoint(
            key.decode("utf-8").replace(name + "-", ""),
            data["cpu_usage_avg"],
            data["cpu_temperature"][0].replace(",", "."),
            data["cpu_usage_per"],
            data["memory_percent"],
            gpu_usage,
            gpu_memory_p,
        )
        data_points.append(dp)
    if last_data == '':
        return
    n = Node(
        name,
        last_data["cpu_cores"],
        last_data["cpu_logical_cores"],
        gpu_name,
        data_points,
        data["system"],
    )
    n.generate_data_for_charts()
    return n


@app.route("/")
def hello_world():
    nodes_data = [get_data_for_node(name) for name in nodes]
    return render_template("index2.html", data=nodes_data)

@app.route('/get_data')
def get_data():
    nodes_data = [get_data_for_node(name).toJSON() for name in nodes]
    return json.dumps(nodes_data)


if __name__ == "__main__":
    app.run(debug=True)
