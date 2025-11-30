# src/utils/retry.py
import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)

def retry(attempts: int = 3, initial_delay: float = 0.5, backoff: float = 2.0, exceptions=(Exception,)):
    """
    Simple exponential-backoff retry decorator.
    Usage: @retry(attempts=3, initial_delay=0.5, backoff=2.0)
    """
    def deco(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exc = None
            for i in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    logger.warning(f"[retry] {fn.__name__} failed (attempt {i+1}/{attempts}): {e}")
                    if i < attempts - 1:
                        time.sleep(delay)
                        delay *= backoff
            logger.error(f"[retry] All {attempts} attempts failed for {fn.__name__}")
            raise last_exc
        return wrapper
    return deco
