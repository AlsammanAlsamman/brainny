import random
import time


def with_backoff(fn, max_tries=5, base=0.5):
    for attempt in range(max_tries):
        try:
            return fn()
        except TransientError:
            time.sleep(base * (2 ** attempt) + random.uniform(0, 0.3))
    raise
