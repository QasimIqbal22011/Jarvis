import time


class Profiler:

    def __init__(self):
        self.times = {}


    def start(self, name):
        self.times[name] = time.perf_counter()


    def stop(self, name):

        if name not in self.times:
            return

        elapsed = (time.perf_counter() - self.times[name]) * 1000

        print(f"[PROFILE] {name}: {elapsed:.1f} ms")

        del self.times[name]