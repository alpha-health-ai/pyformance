import time
import math
from threading import Lock
from .base_metric import BaseMetric
from ..stats.samples import ExpDecayingSample, DEFAULT_SIZE, DEFAULT_ALPHA


class Histogram(BaseMetric):

    """
    A metric which calculates the distribution of a value.
    """

    def __init__(self, size=DEFAULT_SIZE, alpha=DEFAULT_ALPHA, clock=time, sample=None, tags=None):
        """
        Creates a new instance of a L{Histogram}.
        """
        super(Histogram, self).__init__(tags)
        self.lock = Lock()
        self.clock = clock
        if sample is None:
            sample = ExpDecayingSample(size, alpha, clock)
        self.sample = sample
        self.clear()

    def add(self, value):
        """
        Add value to histogram

        :type value: float
        """
        with self.lock:
            self.sample.update(value)
            self.counter = self.counter + 1
            self.max = value if value > self.max else self.max
            self.min = value if value < self.min else self.min
            self.sum = self.sum + value
            self._update_var(value)

    def clear(self):
        "reset histogram to initial state"
        with self.lock:
            self.sample.clear()
            self.counter = 0.0
            self.max = -2147483647.0
            self.min = 2147483647.0
            self.sum = 0.0
            self.var = [-1.0, 0.0]

    def get_count(self):
        "get current value of counter"
        return self.counter

    def get_sum(self):
        "get current sum"
        return self.sum

    def get_max(self):
        "get current maximum"
        return self.max

    def get_min(self):
        "get current minimum"
        return self.min

    def get_mean(self):
        "get current mean"
        if self.counter > 0:
            return self.sum / self.counter
        return 0

    def get_stddev(self):
        "get current standard deviation"
        if self.counter > 0:
            return math.sqrt(self.get_var())
        return 0

    def get_var(self):
        "get current variance"
        if self.counter > 1:
            return self.var[1] / (self.counter - 1)
        return 0

    def get_snapshot(self):
        "get snapshot instance which holds the percentiles"
        return self.sample.get_snapshot()

    def _update_var(self, value):
        old_m, old_s = self.var
        new_m, new_s = [0.0, 0.0]
        if old_m == -1:
            new_m = value
        else:
            new_m = old_m + ((value - old_m) / self.counter)
            new_s = old_s + ((value - old_m) * (value - new_m))
        self.var = [new_m, new_s]
