from datetime import datetime

class Node:
    def __init__(
        self,
        node_name,
        cpu_cores,
        cpu_logical_cores,
        gpu_name,
        data_points,
    ) -> None:
        self.node_name = node_name
        self.cpu_cores = cpu_cores
        self.cpu_logical_cores = cpu_logical_cores
        self.gpu_name = gpu_name
        self.data_points = data_points

    def __str__(self) -> str:
        return f"{self.node_name} - {self.cpu_cores}"

    def generate_data_for_charts(self):
        self.time = []
        self.cpu_usage_avg = []
        self.cpu_temperature = []
        self.cpu_usage_per = []
        self.memory_percent = []
        self.gpu_usage = []
        self.gpu_memory_percent = []
        for d in self.data_points:
            time = int(float(d.time))
            self.time.append(time)
            self.cpu_usage_avg.append(d.cpu_usage_avg)
            self.cpu_temperature.append(float(d.cpu_temperature))
            self.cpu_usage_per.append(d.cpu_usage_per)
            self.memory_percent.append(d.memory_percent)
            self.gpu_usage.append(d.gpu_usage)
            self.gpu_memory_percent.append(d.gpu_memory_percent * 100)
        result = [[self.cpu_usage_per[j][i] for j in range(len(self.cpu_usage_per))] for i in range(len(self.cpu_usage_per[0]))]
        self.cpu_usage_per = result
class DataPoint:
    def __init__(
        self,
        time,
        cpu_usage_avg,
        cpu_temperature,
        cpu_usage_per,
        memory_percent,
        gpu_usage,
        gpu_memory_percent,
    ) -> None:
        self.time = time
        self.cpu_usage_avg = cpu_usage_avg
        self.cpu_temperature = cpu_temperature
        self.cpu_usage_per = cpu_usage_per
        self.memory_percent = memory_percent
        self.gpu_usage = gpu_usage
        self.gpu_memory_percent = gpu_memory_percent
