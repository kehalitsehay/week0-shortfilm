import time


def retry(fn, attempts=3, base=2.0, sleep=time.sleep):
    """Call fn(); on failure wait base**i seconds and retry. Re-raises the last error."""
    for i in range(attempts):
        try:
            return fn()
        except Exception:
            if i == attempts - 1:
                raise
            sleep(base ** i)
