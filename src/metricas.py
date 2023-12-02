class metricas:
    def __init__(self) :
        self.latency = None

    def add_latency(self,latency):
        self.latency = latency